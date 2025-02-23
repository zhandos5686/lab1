import re

def cs(camel_str):
    ss = re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()
    return ss

csi = "CamelCaseExample"
ssi = cs(csi)
print(ssi) 
