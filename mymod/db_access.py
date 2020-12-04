from datetime import date
import json
import re
import os
import psycopg2
from .nlp import NLP
import random


class DBAccess:
    """DBへのデータ追加、データ検索を引き受けるクラス"""

    def __init__(self):
        self._get_connection()
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

    def write_pages_SBJson(self):
        """DBの情報を500個ずつSB用のJson形式で出力する"""
        with self._connection.cursor() as cursor:
            pages_num = self.get_all_pages_count()
            is_unfinished, offset, limit = True, 0, 500
            while is_unfinished:
                cursor.execute(
                    f"SELECT title,body,url,keyword FROM pages INNER JOIN keywords USING (object_id) LIMIT {limit} OFFSET {offset};")
                filename = "./result_file/" + \
                    str(date.today()) + "_" + str(offset) + ".json"
                self._write_pages_SBJson(cursor.fetchall(), filename)
                offset += limit
                is_unfinished = offset < pages_num

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

    def update_keyword(self):
        """keyword列がNULLの物を更新する"""
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT object_id,body FROM pages LEFT OUTER JOIN keywords USING (object_id) WHERE keyword IS NULL;")
            results = cursor.fetchall()
            nlp = NLP()
            for result in results:
                keywords = nlp.collect_keyword(result[1])
                cursor.execute(
                    f"INSERT INTO keywords (object_id,keyword) VALUES ({result[0]},'{keywords}')")
                self._connection.commit()

    def get_title_pages(self, object_id):
        """コレクトしてきた記事からidに紐づくtitleを渡す"""
        with self._connection.cursor() as cursor:
            cursor.execute(
                f"SELECT title FROM pages WHERE object_id={object_id};")
            result = cursor.fetchone()
            return result[0]

    def update_interest(self, object_id, change_interest):
        with self._connection.cursor() as cursor:
            cursor.execute(
                f"SELECT interest_index FROM interests WHERE object_id={object_id};")
            add_value = f"interest_index+{change_interest}" if cursor.fetchone()[
                0] else f"{change_interest}"
            cursor.execute(
                f"UPDATE interests SET interest_index={add_value} WHERE object_id={object_id};")
            self._connection.commit()

    def pick_id_body_pages(self, offset=None, limit=None):
        with self._connection.cursor() as cursor:
            q_offset = f" OFFSET {offset} " if offset else ""
            q_limit = f" LIMIT {limit} " if limit else ""
            query = "SELECT object_id,body FROM pages" + q_offset + q_limit + ";"
            cursor.execute(query)
            return cursor.fetchall()

    def random_get_interest_id(self):
        pages_num = self.get_all_pages_count()
        selected_id = random.randrange(int(pages_num)) + 1
        return selected_id

    def get_all_pages_count(self):
        with self._connection.cursor() as cursor:
            cursor.execute(
                f"SELECT count(object_id) FROM pages;")
            return cursor.fetchone()[0]
