from mymod import d2v
from mymod import db_access

if __name__ == "__main__":
    _db = db_access.DBAccess()
    _d2v = d2v.D2V()

    _d2v.training()

    while True:
        unchecked_article = _db.get_id_interest_null()
        print("base : ", _db.get_title(unchecked_article))
        _input = input("interest? yes : 1 no : other ->")
        interest = True if _input == "1" else False
        _db.update_interest(unchecked_article, interest)

        similer_ids = _d2v.find_similer_articles(unchecked_article)
        for _id in similer_ids:
            print(_db.get_title(_id))
            _db.update_interest(_id, interest)
