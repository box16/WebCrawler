from mymod import db_access

if __name__ == "__main__":
    db = db_access.DBAccess()
    db.write_pages_SBJson()
