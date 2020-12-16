from .db_access import DBAccess
from .nlp import NLP
import os
import collections


class FindInterest:
    def __init__(self):
        self._interest_file = os.environ.get("INTERESTFILE")
        self._not_interest_file = os.environ.get("NOTINTERESTFILE")
        self._interest_words = self._read_words_file(self._interest_file)
        self._not_interest_words = self._read_words_file(
            self._not_interest_file)
        self._not_interest_words_num = len(self._not_interest_words)
        self._exists_words = (len(self._interest_words) +
                              self._not_interest_words_num) > 0
        self._nlp = NLP()
        self._db = DBAccess()
        self._read_scored_info()

    def _read_words_file(self, file_name):
        with open(file_name, "r") as f:
            reads = f.readlines()
            result = {i.strip() for i in reads}
            return result

    def _write_words_file(self, file_name, words):
        with open(file_name, "w") as f:
            for word in words:
                f.write(word + "\n")

    def _read_scored_info(self):
        with open(os.environ.get("SCOREINFOFILE"), "r") as f:
            reads = f.readlines()
            result = [line.split(",") for line in reads]
            self._average = float(result[0][1].strip())
            self._std = float(result[1][1].strip())

    def scored_interest_index(self, text):
        if not self._exists_words:
            return 61
        mors = set(self._nlp.analyze_morphological(text))
        in_interest_num = len(mors & self._interest_words)
        in_not_interest_num = len(mors & self._not_interest_words)
        _x = in_interest_num + \
            (self._not_interest_words_num - in_not_interest_num)
        score = (10 * (_x - self._average) / self._std) + 50
        return score

    def _morphological_words(self, id_set):
        words = []
        for pick in id_set:
            body = self._db.pick_body(pick[0])
            mors = self._nlp.analyze_morphological(body)
            words += mors
        collection_dic = collections.Counter(words)
        result = {key for key, value in collection_dic.items() if value >= 10}
        return result

    def record_interest_word(self):
        interest_id_list = self._db.get_twenty_percent(True)
        not_interests_id_list = self._db.get_twenty_percent(False)

        interest_words_set = self._morphological_words(interest_id_list)
        not_interest_words_set = self._morphological_words(
            not_interests_id_list)

        interest_unique = (
            self._interest_words | (
                interest_words_set -
                not_interest_words_set))
        not_interest_unique = (
            self._not_interest_words | (
                not_interest_words_set -
                interest_words_set))

        interest_unique = interest_unique - not_interest_unique
        not_interest_unique = not_interest_unique - interest_unique

        self._write_words_file(self._interest_file, interest_unique)
        self._write_words_file(self._not_interest_file, not_interest_unique)
