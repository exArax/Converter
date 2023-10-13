import os
import random
import string
import json
import requests
import base64
from requests.exceptions import HTTPError
from converter_package import Kafka_Producer
from dotenv import load_dotenv
from converter_package import Converter
from converter_package import Parser
from converter_package import MatchingModel
from converter_package import ActionModel
from converter_package import ID
from converter_package import WorkflowModel
from converter_package import Image


def deployment(jsonResponse):
    # Parse Intermediate Model
    nodelist, imagelist, application_version = Parser.ReadFile(jsonResponse)

    # Create the namespace that describes the appInstanceInfo
    application_instance = ID.generate_k3s_namespace(name, application_version, randomApplicationIntanceID())

    # minicloud that is decided through matchmaking process
    minicloud = "minicloud5"
    externalIP = "1.2.4.114"
    # model for orchestrator that has the requirements of components
    matchmaking_model = MatchingModel.generate(nodelist, application_instance)
    gpu_list = []
    if name == 'ovr':
        # name of the GPU model (retrieved from RID)
        # since we could have many application components that would require GPUs this variable may have to be a list
        gpu_models = ["nvidia.com/TU117_GEFORCE_GTX_1650"]
        matchmaking_components = matchmaking_model.get(application_instance)
        for component in matchmaking_components:
            component_name = component.get('component')
            host = component.get('host')
            requirements = host.get('requirements')
            hardware_requirements = requirements.get('hardware_requirements')
            if hardware_requirements.get('gpu'):
                gpu = hardware_requirements.get('gpu')
                gpu_brand = gpu.get('brand')
                for gpu_model in gpu_models:
                    if gpu_brand in gpu_model:
                        gpu_dict = {'component': component_name, 'gpu_model': gpu_model}
                        gpu_list.append(gpu_dict)

    # Generate configuration files for Orchestrator
    namespace_yaml = Converter.namespace(application_instance)
    secret_yaml = Converter.secret_generation(json_base64_string, application_instance)
    # gpu_model is an optional parameter
    deployment_files, persistent_files, service_files = Converter.tosca_to_k8s(nodelist, imagelist,
                                                                               application_instance, minicloud,
                                                                               externalIP, gpu_list)

    # model for lifecycle manager that has actions, their order and related components
    actions_set = ActionModel.generate(nodelist, application_instance)

    print(actions_set)
    # workflows for lifecycle manager
    workflows_set = WorkflowModel.generate(nodelist, application_instance)
    print(workflows_set)
    print(namespace_yaml)
    print(secret_yaml)
    print(deployment_files)
    print(matchmaking_model)

    producer = Kafka_Producer.Producer()
    # send json string to broker
    producer.send_message('accordion.monitoring.reservedResources', matchmaking_model,
                          'continuum.accordion-project.eu', '9092')
    print(persistent_files)
    print(service_files)

# Generate a random ID to emulate the application instance ID
def randomApplicationIntanceID():
    S = 5  # number of characters in the string.
    # call random.choices() string module to find the string in Uppercase + numeric data.
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=S))
    return str(ran.lower())


def callAppBucket(json_base64_string, url, name):
    try:
        load_dotenv()
        token_name_value = os.getenv("TOKEN_NAME")
        token_password_value = os.getenv("TOKEN_PASSWORD")
        response = requests.get(url, auth=(token_name_value, token_password_value))

        response.raise_for_status()
        # access JSOn content
        jsonResponse = response.json()
        print("Entire JSON response")
        print(jsonResponse)
        return jsonResponse

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')


def online_selector(name):
    load_dotenv()

    if name == 'plexus':
        url = 'http://app.accordion-project.eu:31724/application?name=plx&isLatest=true'
        token_name = os.getenv("PLEXUS_TOKEN_NAME")
        token_pass = os.getenv("PLEXUS_TOKEN_PASS")

    if name == 'orbk':
        url = 'http://app.accordion-project.eu:31724/application?version=0.0.5&name=uc2orbk'
        token_name = os.getenv("ORBK_TOKEN_NAME")
        token_pass = os.getenv("ORBK_TOKEN_PASS")

    if name == 'ovr':
        url = 'http://app.accordion-project.eu:31724/application?name=ovrxnrh&isLatest=true'
        token_name = os.getenv("OVR_TOKEN_NAME")
        token_pass = os.getenv("OVR_TOKEN_PASS")

    sample_string = token_name + ":" + token_pass
    sample_string_bytes = sample_string.encode("ascii")
    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    print(base64_string)
    json_file = {
        "auths": {
            "https://app.accordion-project.eu:31723": {
                "auth": base64_string
            }
        }
    }
    json_string = json.dumps(json_file)
    json_base64 = base64.b64encode(json_string.encode('utf-8'))
    json_base64_string = json_base64.decode("utf-8")
    return json_base64_string, url, name


json_base64_string,url,name = online_selector("orbk")
jsonresponse =callAppBucket(json_base64_string,url,name)
deployment(jsonresponse)