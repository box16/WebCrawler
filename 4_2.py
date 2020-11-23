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
        # print(f"URL:{self.url}")
        print(f"TITLE:{self.title}")
        # print(f"BODY:{self.body}")
        print("----------")


class Website:
    """クローリングのための情報を格納するクラス

    クローリングのために必要な情報を指定して格納する
    name        クロール対象のWebサイト名
    domain      クロール対象のWebサイトの基点となるURL
    titleTag    クロール対象に特有のページタイトルを抽出するためのCSSコレクタ
    bodyTag     クロール対象に特有の内容を抽出するためのCSSコレクタ
    domeChar    クロール対象の内部ページへのリンクを抽出するための正規表現オブジェクト
    domePage    クロール対象の内部ページへのリンクを作成するためのラムダ式
    """

    def __init__(self, name, domain, titleTag, bodyTag, domeChar, domePage):
        self.name = name
        self.domain = domain
        self.titleTag = titleTag
        self.bodyTag = bodyTag
        self.domeChar = domeChar
        self.domePage = domePage


class Crawler:
    def __init__(self):
        self.site = None
        self.currentURL = None

    def getPage(self, url):
        """指定したURLのBeautifulSoupオブジェクトを返す"""
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.text, "html.parser")

    def getNextPage(self):
        """currentURLから内部ページへのリンクを一つ抽出し、そのページのBeautifulSopuオブジェクトを返す"""
        bs = self.getPage(self.currentURL)
        links = []
        for link in bs.find_all("a", href=self.site.domeChar):
            if "href" in link.attrs:
                links.append(link.attrs["href"])
        NextPageURL = self.site.domePage(random.choice(links))
        self.currentURL = NextPageURL
        return self.getPage(NextPageURL)

    def safeGet(self, pageObj, selector):
        """CSSコレクタを使って指定のタグの中身を抽出する"""
        selectedElems = pageObj.select(selector)
        if (selectedElems is not None) and (len(selectedElems) > 0):
            return '\n'.join([elem.get_text() for elem in selectedElems])

    def parse(self):
        """クロールしたWebページをContentオブジェクトとして生成する"""
        bs = self.getNextPage()
        if bs is not None:
            title = self.safeGet(bs, self.site.titleTag)
            body = self.safeGet(bs, self.site.bodyTag)
            if title != "" and body != "":
                content = Content(self.currentURL, title, body)
                content.printing()

    def startCraw(self, site, collectNum):
        """クロール対象の基点URLから指定数分のWebページをクロールする"""
        self.site = site
        self.currentURL = self.site.domain
        i = 0
        while i < collectNum:
            self.parse()
            i += 1


if __name__ == "__main__":
    web_site_info = [
        {
            "name": "LifeHacker",
            "domain": "https://www.lifehacker.jp/",
            "titleTag": "[class='lh-entryDetail-header'] h1",
            "bodyTag": "[id='realEntryBody'] p",
            "domeChar": re.compile("^(/20)"),
            "domePage": lambda domesticURL: "https://www.lifehacker.jp/" +
            domesticURL,
        },
    ]
    LifeHacker = Website(**web_site_info[0])

    Crawler().startCraw(LifeHacker, 10)
