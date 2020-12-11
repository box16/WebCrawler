from mymod import d2v
from mymod import db_access
from mymod import nlp
import collections


def morphological_words(id_set):
    words = []
    for pick in id_set:
        body = _db.pick_body(pick[0])
        mors = _nlp.analyze_morphological(body)
        words += mors
    collection_dic = collections.Counter(words)
    return collection_dic


def write_file(file_name, _set):
    with open(file_name, "w") as f:
        for word in _set:
            f.write(word + "\n")


if __name__ == "__main__":
    _db = db_access.DBAccess()
    _d2v = d2v.D2V()
    _nlp = nlp.NLP()

    tops = _db.get_twenty_percent(True)
    worsts = _db.get_twenty_percent(False)

    top_words_set = morphological_words(tops)
    worst_words_set = morphological_words(worsts)

    top_picks = {key for key, value in top_words_set.items() if value >= 10}
    worst_picks = {key for key, value in worst_words_set.items()
                   if value >= 10}

    top_unique = top_picks - worst_picks
    write_file("interest_words.txt", top_unique)
    worst_unique = worst_picks - top_picks
    write_file("not_interest_words.txt", worst_unique)
