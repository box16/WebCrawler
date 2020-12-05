import requests
from bs4 import BeautifulSoup
import random
import json
from .db_access import DBAccess
import logging


class Website:
    """クローリングのための情報を格納するクラス

    name         クロール対象のWebサイト名\n
    domain       クロール対象のWebサイトの基点となるURL\n
    title_tag    クロール対象に特有のページタイトルを抽出するためのCSSコレクタ\n
    body_tag     クロール対象に特有の内容を抽出するためのCSSコレクタ\n
    dome_char    クロール対象の内部ページへのリンクを抽出するための正規表現オブジェクト\n
    dome_page    クロール対象の内部ページへのリンクを作成するためのラムダ式\n
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
    """指定したWebページから内部ページを抽出し、DBに保存するクラス"""

    def __init__(self):
        self._site = None
        self._current_url = None
        self._db_access = DBAccess()
        self._domestic_pages = []

    def _get_page(self, url):
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            logging.warning(f"requests.get error! URL : {url}")
            return None
        return BeautifulSoup(req.text, "html.parser")

    def _collect_domestic_pages(self, url):
        bs = self._get_page(url)
        if not bs:
            logging.warning(f"bs is None! URL : {url}")
            return
        for link in bs.find_all("a", href=self._site.dome_char):
            if not link.attrs["href"]:
                continue
            domestic_page = self._site.dome_page(link.attrs["href"])
            if domestic_page in self._domestic_pages:
                continue
            self._domestic_pages.append(domestic_page)

    def _safe_get(self, page_obj, selector):
        selected_elems = page_obj.select(selector)
        if (selected_elems is not None) and (len(selected_elems) > 0):
            return '\n'.join([elem.get_text() for elem in selected_elems])

    def _scrap(self):
        for page in self._domestic_pages:
            bs = self._get_page(page)
            if not bs:
                logging.warning(f"bs is None! URL : {page}")
                continue
            if not self._db_access.check_dueto_insert(page):
                continue
            title = self._safe_get(bs, self._site.title_tag)
            body = self._safe_get(bs, self._site.body_tag)
            if title != "" and body != "":
                self._db_access.add_page(page, title, body)

    def _initialize(self, site: Website) -> None:
        self._site = site
        self._current_url = None if (site is None) else site.domain
        self._domestic_pages = []

    def start_craw(self, site: Website, deep: int = 10) -> None:
        """クロール対象から指定回数分内部ページをコレクトし、DBに保存する

        基点URL内の内部リンクを全部抽出する\n
        内部リンクからランダムに一つ選び、それを次の基点URLとする\n
        これを引数deep回繰り返す\n
        (デフォルト99,最小1回,最大99回,異常値の場合10回)\n
        """

        assert str(type(site)) == "<class 'mymod.webcraw.Website'>"
        if (deep <= 0) or (deep >= 100):
            logging.info(f"deep num fixed 10")
            deep = 10

        self._initialize(site)
        for trial in range(deep):
            logging.debug(f"{self.site.name} ... {trial}/{deep}")
            self._collect_domestic_pages(self._current_url)
            if not self._domestic_pages:
                continue
            self._current_url = random.choice(self._domestic_pages)
        self._scrap()
        self._initialize(None)
