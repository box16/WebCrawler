from mylib import webcraw
from mylib import db_access
from define import website_define
from time import sleep

if __name__ == "__main__":
    web_sites = website_define.web_sites
    crawler = webcraw.Crawler()
    for site in web_sites:
        _website = webcraw.Website(**site)
        crawler.start_craw(_website)
