# Converter

Converter is a reasoner for CEAML (Cloud Edge Application Modelling Language). CEAML is a TOSCA extension that is able to describe deployment and runtime adaptation of multicomponent applications. Converter is able to parse models written in CEAML and generate K3s files for the deployment of the application along with some other helpful submodels that can assist Cloud orchestrators.
.The definitions of CEAML can be found in <a href=https://github.com/exArax/Converter/tree/main/application_models/definitions>application_models/definitions</a> and some examples of models are provided in <a href=https://github.com/exArax/Converter/tree/main/application_models/>application models</a>. 

CEAML and Converter have already been used in the ACCORDION platform. The ACCORDION platform was financially supported by the European Union's Horizon 2020 research and innovation programme through grant agreement no 871793. The platform's vision was to simplify the deployment of applications with diverse requirements spanning the Cloud and Edge continuum. To achieve this goal, the platform employed both K3s and Kubevirt for application deployment, thereby supporting deployment units in the form of pods and virtual machines.
Converter is being used by the Orchestrator and Lifecycle Manager of ACCORDION as a subcomponent in order to translate the application model to K3s configuration files, action models, workflow models and matchmaking models

## Installation

```bash
pip3 install converter-package==2.5
```

## 1. Parse Intermediate Model
```python

nodelist, imagelist, application_version = Parser.ReadFile(jsonResponse)
```
## 2. Create the namespace that describes the appInstanceInfo
```python
 application_instance = ID.generate_k3s_namespace(name, application_version, randomApplicationIntanceID())
```

## 3. How to generate matchmaking model
```python
matchmaking_model = MatchingModel.generate(nodelist, application_instance)
```
## 4. Generate namespace and secrets files for Kubernetes
```python
namespace_yaml = Converter.namespace(application_instance)
secret_yaml = Converter.secret_generation(json_base64_string, application_instance)
```

## 5. Generate deployments, persistenv volumes and services files for Kubernetes
```python
deployment_files, persistent_files, service_files = Converter.tosca_to_k8s(nodelist, imagelist,
                                                                                   application_instance, minicloud,
                                                                                   externalIP, gpu_list)
```
!!! Warning: gpu_model is an optional parameter. Since one or more GPU names may be given to Converter, the parameter has to be a list that would contain application components along with the required GPUs

## 6. Generate the action model
```python
actions_set = ActionModel.generate(nodelist, application_instance)
 ```

## 7. Generate the workflows model
```python
workflows_set = WorkflowModel.generate(nodelist, application_instance)
 ```

## 8. Scale out
```python
json_base64_string, url, name = online_selector('plexus')
intermediate_model = callAppBucket(json_base64_string, url, name)
deployment = Converter.scale_out_to_k8s(componentInfo, intermediate_model)
 ```
## More on Usage
DeployInterface.py is an example of usage for the case of deployment. There is also the ScaleOutInterface.py that presents how to use Converter to create scale out files for ACCORDION, it is available on the ACCORDION's Gitlab


## License
[MIT](https://choosealicense.com/licenses/mit/)