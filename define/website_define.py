import re

web_sites = [{"name": "LifeHacker",
              "domain": "https://www.lifehacker.jp/",
              "title_tag": "[class='lh-entryDetail-header'] h1",
              "body_tag": "[id='realEntryBody'] p",
              "dome_char": re.compile("^(/20)"),
              "dome_page": lambda domestic_url: "https://www.lifehacker.jp/" + domestic_url,
              },
             {"name": "PaleolithicMan",
              "domain": "https://yuchrszk.blogspot.com/",
              "title_tag": "[class='post-title single-title emfont']",
              "body_tag": "[class='post-single-body post-body'] p",
              "dome_char": re.compile("""^(?=https://yuchrszk.blogspot.com/..../.+?)(?!.*archive)(?!.*label).*$"""),
              "dome_page": lambda domestic_url: domestic_url,
              },
             ]
