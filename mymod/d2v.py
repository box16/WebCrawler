from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from .db_access import DBAccess
from .nlp import NLP
import re
import os
from smart_open import open


class Corpus:
    def __init__(self):
        self._nlp = NLP()
        self._db = DBAccess()
        self.pages_num = self._db.get_all_pages_count()

    def _format_for_train(self, text):
        text = re.sub(r"\n", "", text)
        text = re.sub(r"\s", "", text)
        return text

    def __iter__(self):
        for offset in range(self.pages_num):
            pick = self._db.pick_id_body_pages(offset=offset, limit=1)
            body = self._format_for_train(pick[1])
            words = self._nlp.analyze_morphological(body)
            yield TaggedDocument(words=words, tags=[pick[0]])


class D2V:
    def __init__(self):
        self.model_file = os.environ.get("D2VMODEL")
        self.corpus = Corpus()

    def training(self):
        """DBに保存されている記事全てを使って文章ベクトル化する"""
        model = Doc2Vec(
            documents=self.corpus,
            dm=1,
            vector_size=300,
            window=8,
            min_count=10,
            workers=4)
        del(self.corpus)
        model.save(self.model_file)
        model.delete_temporary_training_data(
            keep_doctags_vectors=True, keep_inference=True)

    def find_similer_articles(self, object_id):
        """指定したidに似ているベクトルの他記事を5つピックする"""
        model = Doc2Vec.load(self.model_file)
        return model.docvecs.most_similar(positive={object_id, })
