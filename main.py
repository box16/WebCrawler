from mylib  import webcraw
from define import website_define

if __name__ == "__main__":
    web_sites = website_define.web_sites
    for site in web_sites:
        _website = webcraw.Website(**site)
        webcraw.Crawler().start_craw(_website, 10)