import random
import string

import requests
from requests.exceptions import HTTPError

import ActionModel
import MatchingModel
import Parser
import base64
import json
import Converter


def generateID():
    S = 10  # number of characters in the string.
    # call random.choices() string module to find the string in Uppercase + numeric data.
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=S))
    return str(ran)


def callAppBucket(json_base64_string, url, name):
    try:
        response = requests.get(url)
        response.raise_for_status()
        # access JSOn content
        jsonResponse = response.json()
        print("Entire JSON response")
        print(jsonResponse)
        # Generate a random ID to emulate the running instance ID
        ID = generateID()
        # Parse Intermediate Model
        nodelist, imagelist, application_version = Parser.ReadFile(jsonResponse)
        # Create the namespace that describes the running instance component
        namespace = "accordion-" + name + "-" + application_version + "-" + ID
        # Generate configuration files for Orchestrator
        namespace_yaml = Converter.namespace(namespace)
        secret_yaml = Converter.secret_generation(json_base64_string, namespace)

        # model for orchestrator that has the requirements of components
        matchmaking_model = MatchingModel.generate(nodelist, namespace)
        print(matchmaking_model)

        # minicloud that is decided through matchmaking process
        minicloud = "minicloud5"
        deployment_files, persistent_files, service_files = Converter.tosca_to_k8s(nodelist, imagelist,
                                                                                   namespace, minicloud)

        # model for lifecycle manager that has actions, their order and related components
        actions_set = ActionModel.generate(nodelist, namespace)
        print(actions_set)

        print(namespace_yaml)
        print(secret_yaml)
        print(deployment_files)
        print(matchmaking_model)
        print(persistent_files)
        print(service_files)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')


def selector(name):
    if name == 'plexus':
        url = 'http://app.accordion-project.eu:31724/application?name=UC 3&isLatest=true'
        token_name = 'gitlab+deploy-token-420906'
        token_pass = 'jwCSDnkoZDeZqwf2i9-m'
        jsonResponse = open('intermidietmodel-UC3.json')
    if name == 'orbk':
        url = 'http://app.accordion-project.eu:31724/application?name=UC 2&isLatest=true'
        token_name = 'gitlab+deploy-token-420904'
        token_pass = 'gzP9s2bkJV-yeh1a6fn3'
        jsonResponse = open('intermidietmodel-UC2.json')
    if name == 'ovr':
        url = 'http://app.accordion-project.eu:31724/application?name=UC 1&isLatest=true'
        token_name = 'gitlab+deploy-token-430087'
        token_pass = 'NDxnnzt9WvuR7zyAHchX'
        jsonResponse = open('intermidietmodel-UC1.json')
    sample_string = token_name + ":" + token_pass
    sample_string_bytes = sample_string.encode("ascii")
    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    print(base64_string)
    json_file = {
        "auths": {
            "https://registry.gitlab.com": {
                "auth": base64_string
            }
        }
    }
    json_string = json.dumps(json_file)
    json_base64 = base64.b64encode(json_string.encode('utf-8'))
    json_base64_string = json_base64.decode("utf-8")

    callAppBucket(json_base64_string, url, name)


selector('ovr')
