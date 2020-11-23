import requests
from bs4 import BeautifulSoup
import re
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
    def __init__(self):
        self.site = None
        self.current_url = None

    def get_page(self, url):
        """指定したURLのBeautifulSoupオブジェクトを返す"""
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.text, "html.parser")

    def get_next_page(self):
        """current_urlから内部ページへのリンクを一つ抽出し、そのページのBeautifulSopuオブジェクトを返す"""
        bs = self.get_page(self.current_url)
        links = []
        for link in bs.find_all("a", href=self.site.dome_char):
            if "href" in link.attrs:
                links.append(link.attrs["href"])
        next_page_url = self.site.dome_page(random.choice(links))
        self.current_url = next_page_url
        return self.get_page(next_page_url)

    def safe_get(self, page_obj, selector):
        """CSSコレクタを使って指定のタグの中身を抽出する"""
        selected_elems = page_obj.select(selector)
        if (selected_elems is not None) and (len(selected_elems) > 0):
            return '\n'.join([elem.get_text() for elem in selected_elems])

    def parse(self):
        """クロールしたWebページをContentオブジェクトとして生成する"""
        bs = self.get_next_page()
        if bs is not None:
            title = self.safe_get(bs, self.site.title_tag)
            body = self.safe_get(bs, self.site.body_tag)
            if title != "" and body != "":
                content = Content(self.current_url, title, body)
                content.printing()

    def start_craw(self, site, collect_num):
        """クロール対象の基点URLから指定数分のWebページをクロールする"""
        self.site = site
        self.current_url = self.site.domain
        i = 0
        while i < collect_num:
            self.parse()
            i += 1


if __name__ == "__main__":
    web_sites = [{"name": "LifeHacker",
                  "domain": "https://www.lifehacker.jp/",
                  "title_tag": "[class='lh-entryDetail-header'] h1",
                  "body_tag": "[id='realEntryBody'] p",
                  "dome_char": re.compile("^(/20)"),
                  "dome_page": lambda domestic_url: "https://www.lifehacker.jp/" + domestic_url,
                  },
                 {"name": "PaleolithicMan",
                  "domain": "https://yuchrszk.blogspot.com/",
                  "title_tag": "[class='post-title single-title emfont']",
                  "body_tag": "[class='post-single-body post-body'] p",
                  "dome_char": re.compile("""^(?=https://yuchrszk.blogspot.com/..../.+?)(?!.*archive)(?!.*label).*$"""),
                  "dome_page": lambda domestic_url: domestic_url,
                  },
                 ]

    for site in web_sites:
        _website = Website(**site)
        Crawler().start_craw(_website, 10)
