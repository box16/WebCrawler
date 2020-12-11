from mymod import db_access
from mymod import nlp
import logging
import os
import numpy


def read_file(file_name):
    with open(file_name, "r") as f:
        reads = f.readlines()
        result = {i.strip() for i in reads}
        return result


def write_file(file_name, data):
    with open(file_name, "w") as f:
        f.write(data)


if __name__ == "__main__":
    log_file = os.environ.get("LOGFILE")
    logging.basicConfig(filename=log_file, level=logging.WARNING)

    _db = db_access.DBAccess()
    _nlp = nlp.NLP()

    result_interest = os.environ.get("INTERESTFILE")
    result_worst = os.environ.get("NOTINTERESTFILE")
    top_word = read_file(result_interest)
    worst_word = read_file(result_worst)

    top_num = len(top_word)
    worst_num = len(worst_word)
    total_num = len(top_word) + len(worst_word)

    id_score = {}
    for index in range(_db.get_all_pages_count()):
        id_body = _db.pick_id_body_pages(offset=index, limit=1)
        mors = set(_nlp.analyze_morphological(id_body[0][1]))

        in_interest_num = len(mors & top_word)
        in_worst_num = len(mors & worst_word)

        score = in_interest_num + (worst_num - in_worst_num)

        id_score[id_body[0][0]] = score

    scores = numpy.array([i for i in id_score.values()])
    average = numpy.mean(scores)
    std = numpy.std(scores)

    score_info = {"average": average,
                  "std": std}
    score_file = os.environ.get("SCOREINFOFILE")
    write_file(score_file, score_info)

    for _id, score in id_score.items():
        finally_score = int((10 * (score - average) / std) + 50)
        _db.update_interest_score(_id, finally_score)
