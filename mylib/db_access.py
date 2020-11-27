from datetime import date
import json
import re


class Formatter:
    def __init__(self):
        pass

    def title_format(self, title):
        """改行をすべて消す"""
        title = re.sub(r"^\s*", "", title)
        title = re.sub(r"\s*$", "", title)
        title = re.sub(r"\n", "", title)
        return title

    def body_format(self, body):
        """連続する改行を一つの改行に置換する
           先頭にある改行を削除する
        """
        body = re.sub(r"(\s*\n+\s*)", "\n", body)
        body = re.sub(r"^(\s*\n\s*)", "", body)
        return body


class DBAccess:
    def __init__(self):
        self._out_data = []
        self._formatter = Formatter()

    def add_row(self, url, title, body):
        try:
            dic = {"title": self._formatter.title_format(title),
                   "body": self._formatter.body_format(body),
                   "url": url,
                   }
            self._out_data.append(dic)
        except BaseException:
            print(f"url:{url}\ntitle:{title}\nbody:{body}")

    def temporary_write(self) -> None:
        file_name = "./result_file/" + str(date.today()) + ".json"
        with open(file_name, "w") as f:
            json.dump(self._out_data, f, indent=4, ensure_ascii=False)
