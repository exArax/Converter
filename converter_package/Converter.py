import oyaml as yaml
from converter_package import ID
from converter_package import ComputeNode


def tosca_to_k8s(nodelist, imagelist, application_instance, minicloud, externalIP,gpu_list=[]):
    if not gpu_list:
        gpu_list = None
    images = []
    deployment = {}
    edge_os = ''
    edge_disk = ''
    edge_cpu = ''
    edge_mem = ''
    vm_os = ''
    service_files = []
    persistent_files = []
    deployment_files = []
    vm_flag = False
    print(application_instance)
    resource_list = []
    resources = []
    value = 7000
    y = 0
    for x in nodelist:
        if ('EdgeNode' in x.get_type()) or ('PublicCloud' in x.get_type()):
            resource = ComputeNode.Resource()
            resource.set_os(x.get_os())
            resource.set_cpu(x.get_num_cpu())
            resource.set_mem(x.get_mem_size())
            resource.set_disk(x.get_disk_size())
            resource.set_name(x.get_name())
            if x.get_architecture() == 'x86_64':
                resource.set_arch('amd64')
            else:
                resource.set_arch(x.get_architecture())
            if 'EdgeNode' in x.get_type():
                resource.set_gpu_brand(x.get_gpu_brand())
                resource.set_gpu_dedicated(x.get_gpu_dedicated())
                resource.set_wifi_antenna(x.get_wifi_antenna())
            else:
                resource.set_gpu_brand("None")
                resource.set_gpu_dedicated("None")
                resource.set_wifi_antenna("None")
            resource_list.append(resource)
        if 'Component' in x.get_type():
            accordion_namespace = ID.generate_k3s_pod_name(application_instance, x.get_name(),
                                                           minicloud)
            port_yaml = []
            if x.get_unit() == 'container':
                host = x.get_host()
                for resource in resource_list:
                    if resource.get_cpu() and resource.get_mem() and resource.get_disk():
                        resource_yaml = {
                            'requests': {'cpu': resource.get_cpu(),
                                         'memory': resource.get_mem(),
                                         'ephemeral-storage': resource.get_disk()}}

                    if host == resource.get_name():
                        filelist = []
                        ports = x.get_port()
                        if ports:
                            i = 0
                            for port in ports:
                                i = i + 1
                                content = {'containerPort': int(port.get('port')), 'name': x.get_name() + str(i)}
                                port_yaml.append(content)
                        if x.get_service():
                            service_port = []
                            if ports:
                                for port in ports:
                                    content = {'protocol': port.get('protocol'), 'port': int(port.get('port')),
                                               'targetPort': int(port.get('port'))}
                                    service_port.append(content)

                            service_name = accordion_namespace + "-lb"
                            service = {
                                service_name: {
                                    'apiVersion': 'v1',
                                    'kind': 'Service',
                                    'metadata': {
                                        'name': service_name,
                                        'namespace': application_instance,
                                        'labels': {
                                            'app': application_instance}},
                                    'spec': {
                                        'ports': service_port,
                                        'externalIPs': ['20.121.192.82'],
                                        'selector': {
                                            'component': accordion_namespace},
                                        'type': 'LoadBalancer'}}}
                            if not service_port:
                                service_config = service.get(service_name)
                                spec = service_config.get('spec')
                                spec.pop('ports')
                            service_files.append(service)
                        if x.get_storage_type() == "persistent":
                            persistent_volume = {x.get_volumes_claimname(): {'apiVersion': 'v1',
                                                                             'kind': 'PersistentVolumeClaim',
                                                                             'metadata': {
                                                                                 'name': x.get_volumes_claimname(),
                                                                                 'namespace': application_instance,
                                                                                 'labels': {
                                                                                     'app': application_instance}},
                                                                             'spec':
                                                                                 {'accessModes':
                                                                                      ['ReadWriteOnce'],
                                                                                  'storageClassName': 'local-path',
                                                                                  'resources': {
                                                                                      'requests':
                                                                                          {
                                                                                              'storage': resource.get_disk()}}}}}
                            persistent_files.append(persistent_volume)

                            if port_yaml:
                                deployment = {
                                    accordion_namespace: {'apiVersion': 'apps/v1',
                                                          'kind': 'Deployment',
                                                          'metadata': {
                                                              'name': accordion_namespace,
                                                              'namespace': application_instance,
                                                              'labels': {
                                                                  'app': application_instance,
                                                                  'component': accordion_namespace}},
                                                          'spec': {
                                                              'selector': {
                                                                  'matchLabels': {
                                                                      'app': application_instance,
                                                                      'component': accordion_namespace}},
                                                              'strategy': {
                                                                  'type': 'Recreate'},
                                                              'template': {
                                                                  'metadata': {
                                                                      'labels': {
                                                                          'app': application_instance,
                                                                          'component': accordion_namespace}},
                                                                  'spec': {
                                                                      'containers': [
                                                                          {
                                                                              'image': x.get_image(),
                                                                              'env': [
                                                                                  {
                                                                                      'name': 'ACCORDION_ID',
                                                                                      'value': application_instance}],
                                                                              'name': x.get_name(),
                                                                              'resources': resource_yaml,
                                                                              'imagePullPolicy': 'Always',
                                                                              'ports':
                                                                                  port_yaml,
                                                                              'volumeMounts': [
                                                                                  {
                                                                                      'name': x.get_volumeMounts_name(),
                                                                                      'mountPath': x.get_volumeMounts_path()}]}],
                                                                      'volumes': [{
                                                                          'name': x.get_volumes_name(),
                                                                          'persistentVolumeClaim': {
                                                                              'claimName': x.get_volumes_claimname()}}],
                                                                      'nodeSelector': {
                                                                          'beta.kubernetes.io/os': resource.get_os(),
                                                                          'beta.kubernetes.io/arch': resource.get_arch(),
                                                                          'resource': ''.join(
                                                                              [i for
                                                                               i
                                                                               in
                                                                               resource.get_name()
                                                                               if
                                                                               not i.isdigit()])},
                                                                      'imagePullSecrets': [
                                                                          {
                                                                              'name': application_instance + '-registry-credentials'}]}}}}}
                            if not port_yaml:
                                deployment = {
                                    accordion_namespace: {'apiVersion': 'apps/v1',
                                                          'kind': 'Deployment',
                                                          'metadata': {
                                                              'name': accordion_namespace,
                                                              'namespace': application_instance,
                                                              'labels': {
                                                                  'app': application_instance,
                                                                  'component': accordion_namespace}},
                                                          'spec': {
                                                              'selector': {
                                                                  'matchLabels': {
                                                                      'app': application_instance,
                                                                      'component': accordion_namespace}},
                                                              'strategy': {
                                                                  'type': 'Recreate'},
                                                              'template': {
                                                                  'metadata': {
                                                                      'labels': {
                                                                          'app': application_instance,
                                                                          'component': accordion_namespace}},
                                                                  'spec': {
                                                                      'containers': [
                                                                          {
                                                                              'image': x.get_image(),
                                                                              'env': [
                                                                                  {
                                                                                      'name': 'ACCORDION_ID',
                                                                                      'value': application_instance}],
                                                                              'name': x.get_name(),
                                                                              'resources': resource_yaml,
                                                                              'imagePullPolicy': 'Always',
                                                                              'volumeMounts': [
                                                                                  {
                                                                                      'name': x.get_volumeMounts_name(),
                                                                                      'mountPath': x.get_volumeMounts_path()}]}],
                                                                      'volumes': [{
                                                                          'name': x.get_volumes_name(),
                                                                          'persistentVolumeClaim': {
                                                                              'claimName': x.get_volumes_claimname()}}],
                                                                      'nodeSelector': {
                                                                          'beta.kubernetes.io/os': resource.get_os(),
                                                                          'beta.kubernetes.io/arch': resource.get_arch(),
                                                                          'resource': ''.join(
                                                                              [i for
                                                                               i
                                                                               in
                                                                               resource.get_name()
                                                                               if
                                                                               not i.isdigit()])},
                                                                      'imagePullSecrets': [
                                                                          {
                                                                              'name': application_instance + '-registry-credentials'}]}}}}}
                        if x.get_storage_type() == "ephemeral":

                            if port_yaml:
                                deployment = {
                                    accordion_namespace: {'apiVersion': 'apps/v1',
                                                          'kind': 'Deployment',
                                                          'metadata': {
                                                              'name': accordion_namespace,
                                                              'namespace': application_instance,
                                                              'labels': {
                                                                  'app': application_instance,
                                                                  'component': accordion_namespace}},
                                                          'spec': {
                                                              'selector': {
                                                                  'matchLabels': {
                                                                      'app': application_instance,
                                                                      'component': accordion_namespace}},
                                                              'strategy': {
                                                                  'type': 'Recreate'},
                                                              'template': {
                                                                  'metadata': {
                                                                      'labels': {
                                                                          'app': application_instance,
                                                                          'component': accordion_namespace}},
                                                                  'spec': {
                                                                      'containers': [
                                                                          {
                                                                              'image': x.get_image(),
                                                                              'env': [
                                                                                  {
                                                                                      'name': 'ACCORDION_ID',
                                                                                      'value': application_instance}],
                                                                              'name': x.get_name(),
                                                                              'resources': resource_yaml,
                                                                              'imagePullPolicy': 'Always',
                                                                              'ports':
                                                                                  port_yaml,
                                                                              'volumeMounts': [
                                                                                  {
                                                                                      'name': "cache-volume",
                                                                                      'mountPath': "/cache"}]}],
                                                                      'volumes': [{
                                                                          'name': "cache-volume",
                                                                          'emptyDir': '{}'}],
                                                                      'nodeSelector': {
                                                                          'beta.kubernetes.io/os': resource.get_os(),
                                                                          'beta.kubernetes.io/arch': resource.get_arch(),
                                                                          'resource': ''.join(
                                                                              [i for
                                                                               i
                                                                               in
                                                                               resource.get_name()
                                                                               if
                                                                               not i.isdigit()])},
                                                                      'imagePullSecrets': [
                                                                          {
                                                                              'name': application_instance + '-registry-credentials'}]}}}}}
                            if not port_yaml:
                                deployment = {
                                    accordion_namespace: {'apiVersion': 'apps/v1',
                                                          'kind': 'Deployment',
                                                          'metadata': {
                                                              'name': accordion_namespace,
                                                              'namespace': application_instance,
                                                              'labels': {
                                                                  'app': application_instance,
                                                                  'component': accordion_namespace}},
                                                          'spec': {
                                                              'selector': {
                                                                  'matchLabels': {
                                                                      'app': application_instance,
                                                                      'component': accordion_namespace}},
                                                              'strategy': {
                                                                  'type': 'Recreate'},
                                                              'template': {
                                                                  'metadata': {
                                                                      'labels': {
                                                                          'app': application_instance,
                                                                          'component': accordion_namespace}},
                                                                  'spec': {
                                                                      'containers': [
                                                                          {
                                                                              'image': x.get_image(),
                                                                              'env': [
                                                                                  {
                                                                                      'name': 'ACCORDION_ID',
                                                                                      'value': application_instance}],
                                                                              'name': x.get_name(),
                                                                              'resources': resource_yaml,
                                                                              'imagePullPolicy': 'Always',
                                                                              'volumeMounts': [
                                                                                  {
                                                                                      'name': "cache-volume",
                                                                                      'mountPath': "/cache"}]}],
                                                                      'volumes': [{
                                                                          'name': "cache-volume",
                                                                          'emptyDir': '{}'}],
                                                                      'nodeSelector': {
                                                                          'beta.kubernetes.io/os': resource.get_os(),
                                                                          'beta.kubernetes.io/arch': resource.get_arch(),
                                                                          'resource': ''.join(
                                                                              [i for
                                                                               i
                                                                               in
                                                                               resource.get_name()
                                                                               if
                                                                               not i.isdigit()])},
                                                                      'imagePullSecrets': [
                                                                          {
                                                                              'name': application_instance + '-registry-credentials'}]}}}}}
                        if x.get_storage_type() == "none":

                            if port_yaml:
                                deployment = {
                                    accordion_namespace: {'apiVersion': 'apps/v1',
                                                          'kind': 'Deployment',
                                                          'metadata': {
                                                              'name': accordion_namespace,
                                                              'namespace': application_instance,
                                                              'labels': {
                                                                  'app': application_instance,
                                                                  'component': accordion_namespace}},
                                                          'spec': {
                                                              'selector': {
                                                                  'matchLabels': {
                                                                      'app': application_instance,
                                                                      'component': accordion_namespace}},
                                                              'strategy': {
                                                                  'type': 'Recreate'},
                                                              'template': {
                                                                  'metadata': {
                                                                      'labels': {
                                                                          'app': application_instance,
                                                                          'component': accordion_namespace}},
                                                                  'spec': {
                                                                      'containers': [
                                                                          {
                                                                              'image': x.get_image(),
                                                                              'env': [
                                                                                  {
                                                                                      'name': 'ACCORDION_ID',
                                                                                      'value': application_instance}],
                                                                              'name': x.get_name(),
                                                                              'resources': resource_yaml,
                                                                              'imagePullPolicy': 'Always',
                                                                              'ports':
                                                                                  port_yaml}],
                                                                      'nodeSelector': {
                                                                          'beta.kubernetes.io/os': resource.get_os(),
                                                                          'beta.kubernetes.io/arch': resource.get_arch(),
                                                                          'resource': ''.join(
                                                                              [i for
                                                                               i
                                                                               in
                                                                               resource.get_name()
                                                                               if
                                                                               not i.isdigit()])},
                                                                      'imagePullSecrets': [
                                                                          {
                                                                              'name': application_instance + '-registry-credentials'}]}}}}}
                            if not port_yaml:
                                deployment = {
                                    accordion_namespace: {'apiVersion': 'apps/v1',
                                                          'kind': 'Deployment',
                                                          'metadata': {
                                                              'name': accordion_namespace,
                                                              'namespace': application_instance,
                                                              'labels': {
                                                                  'app': application_instance,
                                                                  'component': accordion_namespace}},
                                                          'spec': {
                                                              'selector': {
                                                                  'matchLabels': {
                                                                      'app': application_instance,
                                                                      'component': accordion_namespace}},
                                                              'strategy': {
                                                                  'type': 'Recreate'},
                                                              'template': {
                                                                  'metadata': {
                                                                      'labels': {
                                                                          'app': application_instance,
                                                                          'component': accordion_namespace}},
                                                                  'spec': {
                                                                      'containers': [
                                                                          {
                                                                              'image': x.get_image(),
                                                                              'env': [
                                                                                  {
                                                                                      'name': 'ACCORDION_ID',
                                                                                      'value': application_instance}],
                                                                              'name': x.get_name(),
                                                                              'resources': resource_yaml,
                                                                              'imagePullPolicy': 'Always',
                                                                          }],
                                                                      'nodeSelector': {
                                                                          'beta.kubernetes.io/os': resource.get_os(),
                                                                          'beta.kubernetes.io/arch': resource.get_arch(),
                                                                          'resource': ''.join(
                                                                              [i for
                                                                               i
                                                                               in
                                                                               resource.get_name()
                                                                               if
                                                                               not i.isdigit()])},
                                                                      'imagePullSecrets': [
                                                                          {
                                                                              'name': application_instance + '-registry-credentials'}]}}}}}

                        deployment = extra_labels(deployment, resource.get_gpu_brand(),
                                                  resource.get_gpu_dedicated(), resource.get_wifi_antenna())
                        deployment_files.append(deployment)
            else:
                host = x.get_host()
                vm_flag = True
                for resource in resource_list:
                    if resource.get_cpu() and resource.get_mem() and resource.get_disk():
                        resource_yaml = {
                            'requests': {'cpu': resource.get_cpu(),
                                         'memory': resource.get_mem(),
                                         'ephemeral-storage': resource.get_disk()}}

                    if host == resource.get_name():
                        if x.get_storage_type() == "persistent":
                            persistent_volume = {x.get_volumes_claimname(): {'apiVersion': 'v1',
                                                                             'kind': 'PersistentVolumeClaim',
                                                                             'metadata': {
                                                                                 'name': 'winhd',
                                                                                 'namespace': application_instance},
                                                                             'spec':
                                                                                 {'accessModes':
                                                                                      ['ReadWriteOnce'],
                                                                                  'storageClassName': 'local-path',
                                                                                  'resources': {
                                                                                      'requests':
                                                                                          {
                                                                                              'storage': resource.get_disk()}}}}}
                            persistent_files.append(persistent_volume)
                        if x.get_service():
                            if x.get_service():
                                service_port = []
                                ports = x.get_port()
                                for port in ports:
                                    content = {'protocol': port.get('protocol'), 'port': int(port.get('port')),
                                               'targetPort': int(port.get('port'))}
                                    service_port.append(content)

                                    service_name = accordion_namespace + "-lb"
                                    service = {
                                        service_name: {
                                            'apiVersion': 'v1',
                                            'kind': 'Service',
                                            'metadata': {
                                                'name': service_name,
                                                'namespace': application_instance,
                                                'labels': {
                                                    'app': application_instance}},
                                            'spec': {
                                                'externalTrafficPolicy': 'Cluster',
                                                'ports': service_port,
                                                'selector': {
                                                    'component': accordion_namespace},
                                                'type': 'LoadBalancer'}}}
                                service_files.append(service)
                        for gpu in gpu_list:
                            component = gpu.get('component')
                            if component not in accordion_namespace:
                                deployment = {
                                        application_instance + "-" + x.get_name() + "-" + minicloud: {
                                            'apiVersion': 'kubevirt.io/v1',
                                            'kind': 'VirtualMachine',
                                            'metadata': {
                                                'name': accordion_namespace,
                                                'namespace': application_instance,
                                                'labels': {
                                                    'kubevirt.io/os': 'linux'}},
                                            'spec': {
                                                'running': True,
                                                'template': {
                                                    'metadata': {
                                                        'name': accordion_namespace,
                                                        'namespace': application_instance,
                                                        'labels': {
                                                            'app': 'monitorable-vm-windows-exporter',
                                                            'component': accordion_namespace,
                                                            'kubevirt.io/domain': x.get_flavor()}},
                                                    'spec': {'nodeSelector': {
                                                        'beta.kubernetes.io/os': resource.get_os(),
                                                        'beta.kubernetes.io/arch': resource.get_arch()},
                                                        'domain': {'cpu': {
                                                            'cores': int(
                                                                resource.get_cpu())},
                                                            'devices': {
                                                                'disks': [{
                                                                    'disk': {
                                                                        'bus': 'sata'},
                                                                    'name': 'disk0'},
                                                                    {'cdrom': {
                                                                        'bus': 'sata'},
                                                                        'name': 'virtiocontainerdisk'}

                                                                ]},
                                                            'machine': {
                                                                'type': 'q35'},
                                                            'resources': {
                                                                'requests': {
                                                                    'memory': resource.get_mem()}}},
                                                        'volumes': [
                                                            {
                                                                'name': 'disk0',
                                                                'persistentVolumeClaim': {
                                                                    'claimName': 'imp-w2k12-vm'}},
                                                            {
                                                                'name': 'virtiocontainerdisk',
                                                                'containerDisk': {
                                                                    'image': 'kubevirt/virtio-container-disk'}},
                                                        ]}}}}}
                                deployment = extra_labels(deployment, resource.get_gpu_brand(),
                                                          resource.get_gpu_dedicated(), resource.get_wifi_antenna())
                            else:
                                gpu_model = gpu.get('gpu_model')
                                deployment = {
                                    application_instance + "-" + x.get_name() + "-" + minicloud: {
                                        'apiVersion': 'kubevirt.io/v1',
                                        'kind': 'VirtualMachine',
                                        'metadata': {
                                            'name': accordion_namespace,
                                            'namespace': application_instance,
                                            'labels': {
                                                'kubevirt.io/os': 'linux'}},
                                        'spec': {
                                            'running': True,
                                            'template': {
                                                'metadata': {
                                                    'name': accordion_namespace,
                                                    'namespace': application_instance,
                                                    'labels': {
                                                        'app': 'monitorable-vm-windows-exporter',
                                                        'component': accordion_namespace,
                                                        'kubevirt.io/domain': x.get_flavor()}},
                                                'spec': {'nodeSelector': {
                                                    'beta.kubernetes.io/os': resource.get_os(),
                                                    'beta.kubernetes.io/arch': resource.get_arch()},
                                                    'domain': {'cpu': {
                                                        'cores': int(
                                                            resource.get_cpu())},
                                                        'devices': {
                                                            'disks': [{
                                                                'disk': {
                                                                    'bus': 'sata'},
                                                                'name': 'disk0'},
                                                                {'cdrom': {
                                                                    'bus': 'sata'},
                                                                    'name': 'virtiocontainerdisk'}

                                                            ], 'gpus': [
                                                                {'name': 'gpu1', 'deviceName': gpu_model}]},
                                                        'machine': {
                                                            'type': 'q35'},
                                                        'resources': {
                                                            'requests': {
                                                                'memory': resource.get_mem()}}},
                                                    'volumes': [
                                                        {
                                                            'name': 'disk0',
                                                            'persistentVolumeClaim': {
                                                                'claimName': 'imp-w2k12-vm'}},
                                                        {
                                                            'name': 'virtiocontainerdisk',
                                                            'containerDisk': {
                                                                'image': 'kubevirt/virtio-container-disk'}},
                                                    ]}}}}}


                                deployment = extra_labels(deployment, resource.get_gpu_brand(),
                                                          resource.get_gpu_dedicated(), resource.get_wifi_antenna())
                        deployment_files.append(deployment)
    if vm_flag:
        exporter_service = {
            application_instance + "-" + x.get_name() + "-" + minicloud + "-exporter-service": {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "monitorable-vm-windows-exporter",
                    "namespace": application_instance,
                    "labels": {
                        "app": "monitorable-vm-windows-exporter"
                    }
                },
                "spec": {
                    "ports": [
                        {
                            "name": "metrics",
                            "targetPort": 9182,
                            "port": 9182
                        }
                    ],
                    "selector": {
                        "app": "monitorable-vm-windows-exporter"
                    }
                }
            }}
        service_files.append(exporter_service)
    return deployment_files, persistent_files, service_files


def secret_generation(json, application):
    secret = {application: {'apiVersion': 'v1',
                            'kind': 'Secret',
                            'metadata': {
                                'name': application + '-registry-credentials',
                                'namespace': application},
                            'type': 'kubernetes.io/dockerconfigjson',
                            'data': {
                                '.dockerconfigjson': json}}}
    return secret


def namespace(application):
    namespace = {
        application: {'apiVersion': 'v1', 'kind': 'Namespace',
                      'metadata': {'name': application}}}

    return namespace


def extra_labels(deployment_file, gpu_model, gpu_dedicated, wifi_antennas):
    if gpu_model != "None" and gpu_dedicated != "None":
        key = deployment_file.keys()
        for k in key:
            file = deployment_file[k]
            spec = file['spec']
            template = spec['template']
            template_spec = template['spec']
            nodeselector = template_spec['nodeSelector']
            if "NVIDIA" in gpu_model:
                gpu_model = "nvidia"

            nodeselector['GPU.model'] = gpu_model
            nodeselector['GPU.dedicated'] = str(gpu_dedicated).lower()

    if wifi_antennas != "None":
        key = deployment_file.keys()
        for k in key:
            file = deployment_file[k]
            spec = file['spec']
            template = spec['template']
            template_spec = template['spec']
            nodeselector = template_spec['nodeSelector']
            nodeselector['Wifi.External.Antenna'] = str(wifi_antennas).lower()
    return deployment_file
