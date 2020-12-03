from mymod import webcraw
from mymod import d2v
from define import website_define

if __name__ == "__main__":
    web_sites = website_define.web_sites
    crawler = webcraw.Crawler()
    for site in web_sites:
        _website = webcraw.Website(**site)
        crawler.start_craw(_website, 50)
    del(web_sites)
    del(crawler)
