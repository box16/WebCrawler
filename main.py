from mymod import webcraw
from mymod import db_access
from mymod import d2v
from define import website_define
from time import sleep

if __name__ == "__main__":
    web_sites = website_define.web_sites
    crawler = webcraw.Crawler()
    for site in web_sites:
        _website = webcraw.Website(**site)
        crawler.start_craw(_website, 1)
    machine = d2v.D2V()
    machine.training()
    #db = db_access.DBAccess()
    # db.update_keyword()
