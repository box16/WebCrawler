from mymod import webcraw
from mymod import d2v
from define import website_define
import logging
import os

if __name__ == "__main__":
    log_file = os.environ.get("LOGFILE")
    logging.basicConfig(filename=log_file, level=logging.WARNING)

    web_sites = website_define.web_sites
    crawler = webcraw.Crawler()

    for site in web_sites:
        _website = webcraw.Website(**site)
        crawler.start_craw(_website, 50)

