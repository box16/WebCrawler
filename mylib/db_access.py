from .webcraw import Content 
from datetime import date
import json

class DBAccess:
    def __init__(self):
        pass
    
    def temporary_write(self,contents : Content) -> None:
        pages = []
        for content in contents:
            #この時に整形
            dic = {}
            dic["title"] = content.title
            dic["lines"] = content.body.splitlines() + [content.url]
            pages.append(dic)

        result = {"pages" : pages}
        file_name = "../result_json" + str(date.today()) + ".json"
        with open(file_name,"w") as f:
            json.dump(result,f,indent=4,ensure_ascii=False)

