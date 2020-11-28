import MeCab
import re
import os


class KeyWordCollector():

    def __init__(self):
        path = os.environ.get("MECABDIC")
        self._mecab_dic = MeCab.Tagger(f'--unk-feature "unknown" -d {path}')

    def collect_keyword(self, text):
        self._mecab_dic.parse("")
        text = self._text_cleaner(text)
        node = self._mecab_dic.parseToNode(text)

        result_nouns = []
        while node:
            if self._is_legal(node):
                result_nouns.append(node.surface)
            node = node.next

        result_nouns = list(set(result_nouns))
        result_text = ""
        for noun in result_nouns:
            result_text += noun + "\n"
        return result_text

    def _is_legal(self, node):
        if node.feature == "unknown":
            return False

        is_noun = (node.feature.split(",")[0] == "名詞")
        is_proprietary = (node.feature.split(",")[1] == "固有名詞")
        is_legal_word_length = (len(node.surface) >= 2)
        is_origin = (node.surface == node.feature.split(",")[6])
        is_teki_in = ("的" in node.surface)
        return is_noun and is_legal_word_length and is_proprietary and is_origin and not is_teki_in

    def _text_cleaner(self, text):
        text = re.sub(r'[!-~]', "", text)
        text = re.sub(r'[︰-＠]', "", text)
        text = re.sub('\n', " ", text)
        return text
