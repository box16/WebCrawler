from .db_access import DBAccess
from .nlp import NLP
import os
import collections

class FindInterest:
    def __init__(self):
        self._interest_file  = os.environ.get("INTERESTFILE")
        self._worst_file     = os.environ.get("NOTINTERESTFILE")
        self._interest_words = self._read_words_file(self._interest_file)
        self._worst_words    = self._read_words_file(self._worst_file)
        self._worst_words_num = len(self._worst_words)
        self._exists_words   = (len(self._interest_words) + self._worst_words_num) > 0
        self._nlp = NLP()
        self._db = DBAccess()
        self._read_scored_info()

    def _read_words_file(self,file_name):
        with open(file_name, "r") as f:
            reads = f.readlines()
            result = {i.strip() for i in reads}
            return result

    def _write_words_file(self,file_name,words):
        with open(file_name, "w") as f:
            for word in words:
                f.write(word + "\n")    
    
    def _read_scored_info(self):
        with open(os.environ.get("SCOREINFOFILE"), "r") as f:
            reads = f.readlines()
            result = [line.split(",") for line in reads]
            self._average = float(result[0][1].strip())
            self._std = float(result[1][1].strip())
    
    def scored_interest_index(self,text):
        if not self._exists_words:
            return 61
        mors = set(self._nlp.analyze_morphological(text))
        in_interest_num = len(mors & self._interest_words)
        in_worst_num = len(mors & self._worst_words)
        _x = in_interest_num + (self._worst_words_num - in_worst_num)
        score = (10*(_x - self._average)/self._std) + 50
        return score
    
    def _morphological_words(self,id_set):
        words = []
        for pick in id_set:
            body = self._db.pick_body(pick[0])
            mors = self._nlp.analyze_morphological(body)
            words += mors
        collection_dic = collections.Counter(words)
        return collection_dic

    def find_interest_word(self):
        interests = self._db.get_twenty_percent(True)
        worsts = self._db.get_twenty_percent(False)

        interest_words_set = self._morphological_words(interests)
        worst_words_set = self._morphological_words(worsts)

        interest_picks = {key for key, value in interest_words_set.items() if value >= 10}
        worst_picks = {key for key, value in worst_words_set.items()if value >= 10}

        interest_unique = (self._interest_words | (interest_picks - worst_picks))
        worst_unique = (self._worst_words | (worst_picks - interest_picks))
        interest_unique = interest_unique - worst_unique
        worst_unique = worst_unique - interest_unique
        self._write_words_file(self._interest_file, interest_unique)
        self._write_words_file(self._worst_file, worst_unique)
