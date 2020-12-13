import requests
from bs4 import BeautifulSoup
import random
import json
import re
from .db_access import DBAccess
from .find_interest import FindInterest
import logging


class Website:
    """クローリングのための情報を格納するクラス

    name         クロール対象のWebサイト名\n
    domain       クロール対象のWebサイトの基点となるURL\n
    title_tag    クロール対象に特有のページタイトルを抽出するためのCSSコレクタ\n
    body_tag     クロール対象に特有の内容を抽出するためのCSSコレクタ\n
    extractor    クロール対象の内部ページへのリンクを抽出するための正規表現オブジェクト\n
    url_maker    クロール対象の内部ページへのリンクを作成するためのラムダ式\n
    """

    def __init__(
            self,
            name,
            domain,
            title_tag,
            body_tag,
            extractor,
            url_maker):
        self.name = name
        self.domain = domain
        self.title_tag = title_tag
        self.body_tag = body_tag
        self.extractor = extractor
        self.url_maker = url_maker


class Crawler:
    """指定したWebページから内部ページを抽出し、DBに保存するクラス"""

    def __init__(self):
        pass

    def _get_page(self, url):
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            logging.warning(f"requests.get error! URL : {url}")
            return None
        return BeautifulSoup(req.text, "html.parser")

    def _collect_domestic_pages(
            self,
            url=None,
            url_list=[],
            extractor=None,
            url_maker=None):
        bs = self._get_page(url)
        if not bs:
            logging.warning(f"bs is None! URL : {url}")
            return
        for link in bs.find_all("a", href=extractor):
            if not link.attrs["href"]:
                continue
            other_url = url_maker(link.attrs["href"])
            other_url = re.sub(r"/$", "", other_url)
            if other_url in url_list:
                continue
            url_list.append(other_url)

    def _safe_get(self, page_obj, selector):
        selected_elems = page_obj.select(selector)
        if (selected_elems is not None) and (len(selected_elems) > 0):
            return '\n'.join([elem.get_text() for elem in selected_elems])

    def _scrap(self, url_list=[], body_tag=None, title_tag=None):
        result_pages = []
        for url in url_list:
            bs = self._get_page(url)
            if not bs:
                logging.warning(f"bs is None! URL : {url}")
                continue
            body = self._safe_get(bs, body_tag)
            title = self._safe_get(bs, title_tag)
            if title != "" and body != "":
                page_info = {"url": url,
                             "title": title,
                             "body": body, }
                result_pages.append(page_info)
        return result_pages

    def start_craw(self, site, deep=10):
        """クロール対象から指定回数分内部ページをコレクトし、DBに保存する

        基点URL内の内部リンクを全部抽出する\n
        内部リンクからランダムに一つ選び、それを次の基点URLとする\n
        これを引数deep回繰り返す\n
        (デフォルト99,最小1回,最大99回,異常値の場合10回)\n
        """

        assert str(type(site)) == "<class 'mymod.webcraw.Website'>"
        if (deep <= 0) or (deep >= 100):
            deep = 10

        url_list = []
        current_url = site.domain
        trial = 0

        while trial < deep:
            self._collect_domestic_pages(
                url=current_url,
                url_list=url_list,
                extractor=site.extractor,
                url_maker=site.url_maker)
            if not url_list:
                continue
            current_url = random.choice(url_list)
            trial += 1
        result_pages = self._scrap(
            url_list=url_list,
            body_tag=site.body_tag,
            title_tag=site.title_tag)
        return result_pages
