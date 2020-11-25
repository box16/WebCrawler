import requests
from bs4 import BeautifulSoup
import random
import datetime
import json

class Content:
    """Webページの抽出結果としてURL,タイトル、内容を格納するクラス

    このクラスに保存された内容がファイルやデータベースに保存される
    """

    def __init__(self, url, title, body):
        self.url = url
        self.title = title
        self.body = body

    def printing(self):
        """保存されているWebページ情報を表示する"""
        print("----------")
        print(f"URL:{self.url}")
        print(f"TITLE:{self.title}")
        print(f"BODY:{self.body}")
        print("----------")


class Website:
    """クローリングのための情報を格納するクラス

    クローリングのために必要な情報を指定して格納する
    name         クロール対象のWebサイト名
    domain       クロール対象のWebサイトの基点となるURL
    title_tag    クロール対象に特有のページタイトルを抽出するためのCSSコレクタ
    body_tag     クロール対象に特有の内容を抽出するためのCSSコレクタ
    dome_char    クロール対象の内部ページへのリンクを抽出するための正規表現オブジェクト
    dome_page    クロール対象の内部ページへのリンクを作成するためのラムダ式
    """

    def __init__(
            self,
            name,
            domain,
            title_tag,
            body_tag,
            dome_char,
            dome_page):
        self.name = name
        self.domain = domain
        self.title_tag = title_tag
        self.body_tag = body_tag
        self.dome_char = dome_char
        self.dome_page = dome_page


class Crawler:
    def __init__(self):
        self._site = None
        self._current_url = None
        self._domestic_pages = []
        self._contents = []

    def _get_page(self, url):
        """指定したURLのBeautifulSoupオブジェクトを返す"""
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.text, "html.parser")

    def _collect_domestic_pages(self, url):
        """与えられたURLを基点に内部ページを取得する"""
        bs = self._get_page(url)
        for link in bs.find_all("a", href=self._site.dome_char):
            domestic_page = self._site.dome_page(link.attrs["href"])
            if domestic_page not in self._domestic_pages:
                self._domestic_pages.append(domestic_page)

    def _safe_get(self, page_obj, selector):
        """CSSコレクタを使って指定のタグの中身を抽出する"""
        selected_elems = page_obj.select(selector)
        if (selected_elems is not None) and (len(selected_elems) > 0):
            return '\n'.join([elem.get_text() for elem in selected_elems])

    def _parse(self):
        """クロールしたWebページをContentオブジェクトとして生成する"""
        for page in self._domestic_pages:
            bs = self._get_page(page)
            if bs is None:
                continue
            title = self._safe_get(bs, self._site.title_tag)
            body = self._safe_get(bs, self._site.body_tag)
            if title != "" and body != "":
                content = Content(page, title, body)
                self._contents.append(content)

    def _initialize(self,site : Website) -> None:
        """CrawlするWebサイトをセット、リセットする"""
        self._site = site
        self._current_url = None if (site == None) else site.domain
        self._domestic_pages = []

    def start_craw(self, site : Website, deep : int=2) -> None:
        """クロール対象の基点URLから指定回数分内部ページをコレクトする"""
        self._initialize(site)
        for trial in range(deep):
            self._collect_domestic_pages(self._current_url)
            self._current_url = random.choice(self._domestic_pages)
            print(f"{trial}/{deep}")
        self._parse()
        self._initialize(None)