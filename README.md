# Converter

Converter is a subcomponent of the ACCORDION platform. It is being used by the Orchestrator and Lifecycle Manager components in order to translate the application model to K3s configuration files, action models, workflow models and matchmaking models. The Converter sucomponent requires to have access to Gitlab instance that developers use in ACCORDION. For that reason in the code of the converter there are parts that use an .env file to retrieve the saved tokens. This env file is not commited here, one should consider to generate access tokens in their repositories in order to generate the secrets for the docker images.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip3 install converter-package==1.3
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
## More on Usage
Interface.py is an example of usage, it is available on the ACCORDION's Gitlab
