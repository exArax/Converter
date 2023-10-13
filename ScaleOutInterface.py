from DeployInterface import online_selector, callAppBucket
from converter_package import Converter
import re

scale_out_orbk = {
    "operation": "undeploy",
    "componentInfo": "acc-uc2orbk-0-0-4-00036-gameserver-7reio-min1",
    "timestamp": 123456789,
    "token": "jks8o23rfo2i4"
}


componentInfo = scale_out_orbk.get("componentInfo")
if 'orbk' in componentInfo:
    json_base64_string, url, name = online_selector('orbk')
intermediate_model = callAppBucket(json_base64_string, url, name)
deployment = Converter.undeploy(componentInfo, intermediate_model)
print(deployment)
