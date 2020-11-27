from datetime import date
import json
import re
import os
import psycopg2


class DBAccess:
    def __init__(self):
        self._get_connection()

    def _get_connection(self):
        try:
            database_info = os.environ.get("WEBCRAWLDB")
            self._connection = psycopg2.connect(database_info)
        except BaseException:
            print("DB接続エラー")

    def add_row(self, url, title, body):
        with self._connection.cursor() as cursor:
            title = self._title_format(title)
            body = self._body_format(body)
            cursor.execute(
                f"INSERT INTO pages (url,title,body) VALUES ('{url}','{title}','{body}');")
            self._connection.commit()

    def _title_format(self, title):
        """改行をすべて消す"""
        title = re.sub(r"^\s*", "", title)
        title = re.sub(r"\s*$", "", title)
        title = re.sub(r"\n", "", title)
        title = self._escape_single_quot(title)
        return title

    def _body_format(self, body):
        """連続する改行を一つの改行に置換する
           先頭にある改行を削除する
        """
        body = re.sub(r"(\s*\n+\s*)", "\n", body)
        body = re.sub(r"^(\s*\n\s*)", "", body)
        body = self._escape_single_quot(body)
        return body

    def _escape_single_quot(self, text):
        text = re.sub(r"\'", "", text)
        return text
