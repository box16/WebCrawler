from datetime import date
import json
import re
import os
import psycopg2
from .nlp import NLP


class DBAccess:
    """DBへのデータ追加、データ検索を引き受けるクラス"""

    def __init__(self):
        self._get_connection()
        self._nlp = NLP()
        self._reference_table = ["keywords", "interests"]

    def _get_connection(self):
        try:
            database_info = os.environ.get("WEBCRAWLDB")
            self._connection = psycopg2.connect(database_info)
        except BaseException:
            print("DB接続エラー")

    def add_page(self, url, title, body):
        """渡された情報をDBに保存する

        DBに保存するときに文字列を整形する
        """
        with self._connection.cursor() as cursor:
            if self.check_dueto_insert(url) == False:
                return
            title = self._title_format(title)
            body = self._body_format(body)
            cursor.execute(
                f"INSERT INTO pages (object_id,url,title,body) VALUES (nextval('object_id_seq'),'{url}','{title}','{body}');")
            self._connection.commit()
            self._update_reference_table()

    def _update_reference_table(self):
        with self._connection.cursor() as cursor:
            for table in self._reference_table:
                cursor.execute(
                    f"INSERT INTO {table} (object_id) SELECT object_id FROM pages AS p  WHERE NOT EXISTS (SELECT 1 FROM {table} AS z WHERE p.object_id = z.object_id);")
                self._connection.commit()

    def check_dueto_insert(self, url):
        """urlからデータベースにデータを挿入可能か調べる"""
        with self._connection.cursor() as cursor:
            cursor.execute(f"SELECT url FROM pages WHERE url='{url}';")
            result = cursor.fetchall()
            if result:
                return False
            else:
                return True

    def _title_format(self, title):
        title = re.sub(r"^\s*", "", title)
        title = re.sub(r"\s*$", "", title)
        title = re.sub(r"\n", "", title)
        title = self._escape_single_quot(title)
        return title

    def _body_format(self, body):
        body = re.sub(r"(\s*\n+\s*)", "\n", body)
        body = re.sub(r"^(\s*\n\s*)", "", body)
        body = self._escape_single_quot(body)
        return body

    def _escape_single_quot(self, text):
        text = re.sub(r"\'", " ", text)
        return text

    def update_keyword(self):
        """keyword列がNULLの物を更新する"""
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT object_id,body FROM pages LEFT OUTER JOIN keywords USING (object_id) WHERE keyword IS NULL;")
            results = cursor.fetchall()
            for result in results:
                keywords = self._nlp.collect_keyword(result[1])
                cursor.execute(
                    f"INSERT INTO keywords (object_id,keyword) VALUES ({result[0]},'{keywords}')")
                self._connection.commit()

    def write_pages_SBJson(self):
        """DBの情報を500個ずつSB用のJson形式で出力する"""
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM pages;")
            pages_num = cursor.fetchone()[0]
            is_unfinished, offset, period = True, 0, 500
            while is_unfinished:
                cursor.execute(
                    f"SELECT title,body,url,keyword FROM pages INNER JOIN keywords USING (object_id) LIMIT {period} OFFSET {offset};")
                filename = "./result_file/" + \
                    str(date.today()) + "_" + str(offset) + ".json"
                self._write_pages_SBJson(cursor.fetchall(), filename)
                offset += period
                is_unfinished = offset < pages_num

    def get_all_pages_data(self):
        """コレクトしてきたすべての記事のidと内容を渡す"""
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT object_id,body FROM pages;")
            result = cursor.fetchall()
            return result

    def get_title(self, object_id):
        """コレクトしてきた記事からidに紐づくtitleを渡す"""
        with self._connection.cursor() as cursor:
            cursor.execute(
                f"SELECT title FROM pages WHERE object_id={object_id};")
            result = cursor.fetchone()
            return result[0]

    def _write_pages_SBJson(self, data, filename):
        pages = []
        for page in data:
            keywords = page[3].split("\n")
            link = ""
            for key in keywords:
                if key:
                    link += "#" + re.sub(r"\s", "_", key) + " "
            dic = {"title": page[0],
                   "lines": [page[0]] + page[1].split("\n") + [page[2], link],
                   }
            pages.append(dic)
        outdic = {"pages": pages}

        with open(filename, "w") as f:
            json.dump(outdic, f, indent=4, ensure_ascii=False)

    def get_id_interest_null(self):
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT object_id FROM interests WHERE interest_index IS NULL LIMIT 1;")
            result = cursor.fetchone()
            return result[0]

    def update_interest(self, object_id, change_interest):
        with self._connection.cursor() as cursor:
            cursor.execute(
                f"SELECT interest_index FROM interests WHERE object_id={object_id};")
            if cursor.fetchone()[0]:
                cursor.execute(
                    f"UPDATE interests SET interest_index=interest_index+{change_interest} WHERE object_id={object_id};")
            else:
                cursor.execute(
                    f"UPDATE interests SET interest_index={change_interest} WHERE object_id={object_id};")
            self._connection.commit()
