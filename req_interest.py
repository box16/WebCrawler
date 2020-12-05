from mymod import d2v
from mymod import db_access
import logging
import os

if __name__ == "__main__":
    log_file = os.environ.get("LOGFILE")
    logging.basicConfig(filename=log_file, level=logging.DEBUG)
    _db = db_access.DBAccess()
    _d2v = d2v.D2V()
    print("traing")
    _d2v.training()
    print("traing Done")

    while True:
        unchecked_article = _db.random_get_interest_id()
        print("base : ", _db.get_title_pages(unchecked_article))
        _input = input("interest? yes : 1 no : other ->")
        change_interest = 1 if _input == "1" else -1
        _db.update_interest(unchecked_article, change_interest)

        similer_articles = _d2v.find_similer_articles(unchecked_article)
        for _id, similarity in similer_articles:
            _db.update_interest(_id, change_interest * similarity)

        print()
