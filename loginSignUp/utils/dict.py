from typing import Dict,List
def convert_to_dict(body : List[str])->Dict[str,str]:
    output = {}
    for i in body:
        res = i.split(':')
        output[res[0]] = res[1]
    return output
