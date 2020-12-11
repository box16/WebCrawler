from mymod import db_access
from mymod import nlp
import numpy


def read_file(file_name):
    with open(file_name, "r") as f:
        reads = f.readlines()
        result = [i.strip() for i in reads]
        return result


if __name__ == "__main__":
    _db = db_access.DBAccess()
    _nlp = nlp.NLP()

    interest_word = set(read_file("interest_words.txt"))
    not_interest_word = set(read_file("not_interest_words.txt"))
    interest_num = len(interest_word)
    not_interest_num = len(not_interest_word)
    total_num = len(interest_word) + len(not_interest_word)

    id_score = {}
    for index in range(_db.get_all_pages_count()):
        id_body = _db.pick_id_body_pages(offset=index, limit=1)
        mors = set(_nlp.analyze_morphological(id_body[0][1]))
        in_interest_num = len(mors & interest_word)
        in_not_interest_num = len(mors & not_interest_word)
        score = in_interest_num + (not_interest_num - in_not_interest_num)
        id_score[id_body[0][0]] = score

    scores = numpy.array([i for i in id_score.values()])
    average = numpy.mean(scores)
    std = numpy.std(scores)
    for _id, score in id_score.items():
        finally_score = int((10 * (score - average) / std) + 50)
        _db.update_interest_score(_id, finally_score)
