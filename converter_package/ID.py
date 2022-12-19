import random
import string
import time


def generate_k3s_pod_name(appinstanceinfo, component_name, minicloud_id):
    running_component_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    k3s_pod_name = appinstanceinfo + "-" + component_name + "-" + str(
        running_component_id) + "-" + minicloud_id
    return k3s_pod_name


def generate_k3s_namespace(application_name, application_version, application_id):
    k3s_namespace = "acc-" + application_name + "-" + application_version + "-" + application_id
    return k3s_namespace
