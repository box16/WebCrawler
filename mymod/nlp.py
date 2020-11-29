import MeCab
import re
import os


class KeyWordCollector():

    def __init__(self):
        path = os.environ.get("MECABDIC")
        self._mecab_dic = MeCab.Tagger(f'--unk-feature "unknown" -d {path}')

    def analyze_morphological(self, text):
        node = self._prepare_analyze(text)
        result = []
        while node:
            result.append(node.surface)
            node = node.next
        return result

    def _prepare_analyze(self, text):
        self._mecab_dic.parse("")
        text = self._text_cleaner(text)
        node = self._mecab_dic.parseToNode(text)
        return node

    def collect_keyword(self, text):
        """渡した文字列から特徴的な名詞を抽出する"""
        node = self._prepare_analyze(text)

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
        """単語の中から、特徴を示せるものを抽出する"""
        if node.feature == "unknown":
            return False

        is_noun = (node.feature.split(",")[0] == "名詞")
        is_proprietary = (node.feature.split(",")[1] == "固有名詞")
        is_legal_word_length = (len(node.surface) >= 2)
        is_origin = (node.surface == node.feature.split(",")[6])
        is_teki_in = ("的" in node.surface)
        return is_noun and is_legal_word_length and is_proprietary and is_origin and not is_teki_in

    def _text_cleaner(self, text):
        """単語抽出のため不要な文字を削除する"""
        text = re.sub(r'[!-~]', "", text)
        text = re.sub(r'[︰-＠]', "", text)
        text = re.sub('\n', " ", text)
        return text
