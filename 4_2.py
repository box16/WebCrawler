import requests
from bs4 import BeautifulSoup
import re
import random

class Content:
    def __init__(self, url, title, body):
        self.url = url
        self.title = title
        self.body = body
    
    def printing(self):
        print("----------")
        #print(f"URL:{self.url}")
        print(f"TITLE:{self.title}")
        #print(f"BODY:{self.body}")
        print("----------")

class Website:
    def __init__(self, name, domain, titleTag, bodyTag, domesticChar,domesticPage):
        self.name = name
        self.domain = domain
        self.titleTag = titleTag
        self.bodyTag = bodyTag
        self.domesticChar = domesticChar
        self.domesticPage = domesticPage
        
class Crawler:
    def getPage(self,url):
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.text, "html.parser")
    
    def getNextPage(self,site):
        bs = self.getPage(self.currentURL)
        links = []
        for link in bs.find_all("a",href=site.domesticChar):
            if "href" in link.attrs:
                links.append(link.attrs["href"])
        NextPageURL = site.domesticPage(random.choice(links))
        self.currentURL = NextPageURL
        return self.getPage(NextPageURL)
    
    def safeGet(self,pageObj,selector):
        selectedElems = pageObj.select(selector)
        if (selectedElems is not None) and (len(selectedElems) > 0):
            return '\n'.join([elem.get_text() for elem in selectedElems])
    
    def parse(self, site ,url):
        self.currentURL = site.domain
        for i in range(0,5):
            bs = self.getNextPage(site)
            if bs is not None:
                title = self.safeGet(bs,site.titleTag)
                body = self.safeGet(bs,site.bodyTag)
                if title != "" and body != "":
                    content = Content(url,title,body)
                    content.printing()

if __name__ == "__main__":
    web_site_info = [{"name" : "LifeHacker",
                      "domain" : "https://www.lifehacker.jp/",
                      "titleTag" : "[class='lh-entryDetail-header'] h1",
                      "bodyTag" : "[id='realEntryBody'] p",
                      "domesticChar" : re.compile("^(/20)"),
                      "domesticPage" : lambda domesticURL : "https://www.lifehacker.jp/" + domesticURL,
                    },]
    LifeHacker = Website(**web_site_info[0])

    Crawler().parse(LifeHacker,"https://www.lifehacker.jp/2020/11/amazon-zyplus-tamagottsun.html")
