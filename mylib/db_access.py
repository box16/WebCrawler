from datetime import date
import json
import re
import os
import psycopg2


class DBAccess:
    def __init__(self):
        self._get_connection()

    def _get_connection(self):
        """DBへのコネクションを確立する"""
        try:
            database_info = os.environ.get("WEBCRAWLDB")
            self._connection = psycopg2.connect(database_info)
        except BaseException:
            print("DB接続エラー")

    def add_row(self, url, title, body):
        """渡された情報をDBに保存する

        DBに保存するときに文字列を整形する
        """
        with self._connection.cursor() as cursor:
            if self.check_dueto_insert(url) == False:
                return
            title = self._title_format(title)
            body = self._body_format(body)
            cursor.execute(
                f"INSERT INTO pages (url,title,body) VALUES ('{url}','{title}','{body}');")
            self._connection.commit()

    def check_dueto_insert(self, url):
        """urlからデータベースにデータを挿入可能か調べる
        """
        with self._connection.cursor() as cursor:
            cursor.execute(f"SELECT url FROM pages WHERE url='{url}';")
            result = cursor.fetchall()
            if result:
                return False
            else:
                return True

    def _title_format(self, title):
        """タイトル用のフォーマットを行う

        先頭の空白を全て削除する\n
        末尾の空白を全て削除する\n
        改行を削除する\n
        """
        title = re.sub(r"^\s*", "", title)
        title = re.sub(r"\s*$", "", title)
        title = re.sub(r"\n", "", title)
        title = self._escape_single_quot(title)
        return title

    def _body_format(self, body):
        """ボディ用のフォーマットを行う

        複数の改行を一つの改行に置き換える(改行の前後に空白含む物も可)\n
        先頭の改行を削除する\n
        """
        body = re.sub(r"(\s*\n+\s*)", "\n", body)
        body = re.sub(r"^(\s*\n\s*)", "", body)
        body = self._escape_single_quot(body)
        return body

    def _escape_single_quot(self, text):
        """SQL用にシングルクォートを半角スペースにする"""
        text = re.sub(r"\'", " ", text)
        return text
