import requests
from bs4 import BeautifulSoup
import random


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
        # print(f"BODY:{self.body}")
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
    def __init__(self, site):
        self.site = site
        self.current_url = self.site.domain
        self.domestic_pages = []

    def get_page(self, url):
        """指定したURLのBeautifulSoupオブジェクトを返す"""
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.text, "html.parser")

    def collect_domestic_pages(self, url):
        """与えられたURLを基点に内部ページを取得する"""
        bs = self.get_page(url)
        for link in bs.find_all("a", href=self.site.dome_char):
            domestic_page = self.site.dome_page(link.attrs["href"])
            if domestic_page not in self.domestic_pages:
                self.domestic_pages.append(domestic_page)

    def safe_get(self, page_obj, selector):
        """CSSコレクタを使って指定のタグの中身を抽出する"""
        selected_elems = page_obj.select(selector)
        if (selected_elems is not None) and (len(selected_elems) > 0):
            return '\n'.join([elem.get_text() for elem in selected_elems])

    def parse(self):
        """クロールしたWebページをContentオブジェクトとして生成する"""
        for page in self.domestic_pages:
            bs = self.get_page(page)
            if bs is None:
                continue
            title = self.safe_get(bs, self.site.title_tag)
            body = self.safe_get(bs, self.site.body_tag)
            if title != "" and body != "":
                content = Content(self.current_url, title, body)
                content.printing()

    def start_craw(self, deep=10):
        """クロール対象の基点URLから指定回数分内部ページをコレクトする"""
        i = 0
        while i < deep:
            self.collect_domestic_pages(self.current_url)
            self.current_url = random.choice(self.domestic_pages)
            i += 1
        self.parse()
