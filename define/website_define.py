import re

web_sites = [{"name": "LifeHacker",
              "domain": "https://www.lifehacker.jp/",
              "title_selector": "[class='lh-entryDetail-header'] h1",
              "body_selector": "[id='realEntryBody'] p",
              "extractor": re.compile("^(/20)"),
              "url_maker": lambda domestic_url: "https://www.lifehacker.jp/" + domestic_url,
              },
             {"name": "PaleolithicMan",
              "domain": "https://yuchrszk.blogspot.com/",
              "title_selector": "[class='post-title single-title emfont']",
              "body_selector": "[class='post-single-body post-body']",
              "extractor": re.compile("^(?=https://yuchrszk.blogspot.com/..../.+?)(?!.*archive)(?!.*label).*$"),
              "url_maker": lambda domestic_url: domestic_url,
              },
             {"name": "Gigazine",
              "domain": "https://gigazine.net/",
              "title_selector": "[class='cntimage'] h1",
              "body_selector": "[class='preface']",
              "extractor": re.compile("^(https://gigazine.net/news/20)"),
              "url_maker": lambda domestic_url: domestic_url,
              },
             ]
