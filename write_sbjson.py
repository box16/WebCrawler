from mymod import db_access

if __name__ == "__main__":
    db = db_access.DBAccess()
    db.update_keyword()
    db.write_pages_SBJson()
