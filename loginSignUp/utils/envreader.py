from typing import Dict
def Read_env(file:str)->Dict[str,str]:
    output:Dict[str,str]= {}
    fle = open(file,"r")
    content = fle.readlines()
    fle.close()
    for i in content:
        key,*value = i.split(":")
        output[key] = ''.join(value).strip()
    return output
