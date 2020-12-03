from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from .db_access import DBAccess
from .nlp import NLP
import re
import os


class D2V:
    def __init__(self):
        self._db = DBAccess()
        self._nlp = NLP()
        self.model_file = os.environ.get("D2VMODEL")

    def training(self):
        """DBに保存されている記事全てを使って文章ベクトル化する"""
        documents = self._db.get_all_pages_data()
        training_data = []
        for object_id, body in documents:
            body = self._format_for_train(body)
            words = self._nlp.analyze_morphological(body)
            training_data.append(TaggedDocument(words=words, tags=[object_id]))
        model = Doc2Vec(
            documents=training_data,
            dm=1,
            vector_size=300,
            window=8,
            min_count=10,
            workers=4)
        model.save(self.model_file)

    def find_similer_articles(self, object_id):
        """指定したidに似ているベクトルの他記事を5つピックする"""
        model = Doc2Vec.load(self.model_file)
        return model.docvecs.most_similar(positive={object_id, })

    def _format_for_train(self, text):
        text = re.sub(r"\n", "", text)
        text = re.sub(r"\s", "", text)
        return text
