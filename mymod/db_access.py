from datetime import date
import json
import re
import os
import psycopg2
from .nlp import NLP
import random
import logging


class DBAccess:
    """DBへのデータ追加、データ検索を引き受けるクラス"""

    def __init__(self):
        self._get_connection()
        self._reference_table = ["keywords", "interests","interest_score"]

    def _get_connection(self):
        try:
            database_info = os.environ.get("WEBCRAWLDB")
            self._connection = psycopg2.connect(database_info)
        except BaseException:
            logging.warning(f"DB connection Error!")

    def add_page(self, url, title, body):
        """渡された情報をDBに保存する

        DBに保存するときに文字列を整形する
        """
        with self._connection.cursor() as cursor:
            if not self.check_dueto_insert(url):
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
        if not title:
            logging.warning("title is None")
        return title

    def _body_format(self, body):
        body = re.sub(r"(\s*\n+\s*)", "\n", body)
        body = re.sub(r"^(\s*\n\s*)", "", body)
        body = self._escape_single_quot(body)
        if not body:
            logging.warning("body is None")
        return body

    def _escape_single_quot(self, text):
        text = re.sub(r"\'", " ", text)
        return text

    def write_pages_SBJson(self):
        """DBの情報を500個ずつSB用のJson形式で出力する"""
        with self._connection.cursor() as cursor:
            pages_num = self.get_all_pages_count()
            is_unfinished, offset, limit = True, 0, 2000
            while is_unfinished:
                cursor.execute(
                    f"SELECT p.title,p.body,p.url,k.keyword,i.score FROM pages p INNER JOIN keywords k ON p.object_id=k.object_id INNER JOIN interest_score i ON p.object_id=i.object_id WHERE i.score > 60 LIMIT {limit} OFFSET {offset};")
                filename = "./result_file/" + \
                    str(date.today()) + "_" + str(offset) + ".json"
                self._write_pages_SBJson(cursor.fetchall(), filename)
                offset += limit
                is_unfinished = offset < pages_num

    def _write_pages_SBJson(self, data, filename):
        pages = []
        for page in data:
            if not page[3]:
                continue
            keywords = page[3].split("\n")
            link = ""
            for key in keywords:
                if key:
                    link += "#" + re.sub(r"\s", "_", key) + " "
            dic = {"title": page[0], "lines": [
                page[0], "score_" + str(page[4])] + page[1].split("\n") + [page[2], link], }
            pages.append(dic)
        outdic = {"pages": pages}

        with open(filename, "w") as f:
            json.dump(outdic, f, indent=4, ensure_ascii=False)

    def update_keyword(self):
        """keywordテーブルを更新する"""
        with self._connection.cursor() as cursor:
            all_pages = self.get_all_pages_count()
            nlp = NLP()
            for index in range(all_pages):
                pick = self.pick_id_body_pages(limit=1,offset=index)
                mors = nlp.collect_keyword(pick[0][1])
                cursor.execute(
                    f"UPDATE keywords SET (object_id,keyword) = ({pick[0][0]},'{mors}');")
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
                f"UPDATE interests SET interest_index=interest_index+{change_interest} WHERE object_id={object_id};")
            self._connection.commit()

    def pick_id_body_pages(self, offset=None, limit=None):
        with self._connection.cursor() as cursor:
            q_offset = f" OFFSET {offset} " if offset else ""
            q_limit = f" LIMIT {limit} " if limit else ""
            query = "SELECT object_id,body FROM pages" + q_offset + q_limit + ";"
            cursor.execute(query)
            return cursor.fetchall()

    def random_get_interest_id(self):
        with self._connection.cursor() as cursor:
            cursor.execute(
                f"SELECT object_id FROM interests WHERE interest_index = 0 LIMIT 1;")
            selected_id = cursor.fetchone()[0]
            if selected_id:
                return selected_id
            else:
                print("全てのページに点数がついています")
                pages_num = self.get_all_pages_count()
                selected_id = random.randrange(int(pages_num)) + 1
                return selected_id

    def get_all_pages_count(self):
        with self._connection.cursor() as cursor:
            cursor.execute(
                f"SELECT count(object_id) FROM pages;")
            return cursor.fetchone()[0]

    def get_twenty_percent(self, top=True):
        with self._connection.cursor() as cursor:
            all_num = self.get_all_pages_count()
            twenty = (all_num * 2) // 10
            _sort = "DESC" if top else "ASC"
            condition = "> 0" if top else "< 0"
            cursor.execute(
                f"SELECT object_id FROM interests WHERE interest_index {condition} ORDER BY interest_index {_sort} LIMIT {twenty};")
            return cursor.fetchall()

    def pick_body(self, object_id):
        with self._connection.cursor() as cursor:
            cursor.execute(
                f"SELECT body FROM pages WHERE object_id = {object_id};")
            return cursor.fetchone()[0]

    def update_interest_score(self, object_id, score):
        with self._connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE interest_score SET score={score} WHERE object_id = {object_id};")
            self._connection.commit()
