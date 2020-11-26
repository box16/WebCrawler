from datetime import date
import json

class DBAccess:
    def __init__(self):
        self._out_data = []

    def add_row(self,url,title,body):
        dic = {"title" : title,
               "body" : body,
               "url" : url,
              }
        self._out_data.append(dic)

    def temporary_write(self) -> None:
        file_name = "./result_file/" + str(date.today()) + ".json"
        with open(file_name,"w") as f:
            json.dump(self._out_data,f,indent=4,ensure_ascii=False)