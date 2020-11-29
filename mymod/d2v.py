from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from .db_access import DBAccess
from .nlp import NLP
import re


class D2V:
    def __init__(self):
        self._db = DBAccess()
        self._nlp = NLP()

    def training(self):
        """DBに保存されている記事全てを使って文章ベクトル化する"""
        documents = self._db.get_all_pages_data()
        training_data = []
        for object_id, body in documents:
            body = self._format_for_train(body)
            words = self._nlp.analyze_morphological(body)
            training_data.append(TaggedDocument(words=words, tags=[object_id]))
        print("prepare done")
        model = Doc2Vec(
            documents=training_data,
            dm=1,
            vector_size=300,
            window=8,
            min_count=10,
            workers=4)
        model.save("/home/pi/My_App/Web_Scrap_for_Python/d2v_model/d2v.model")

    def find_similer_articles(self, object_id):
        """指定したidに似ているベクトルの他記事を5つピックする"""
        model = Doc2Vec.load(
            '/home/pi/My_App/Web_Scrap_for_Python/d2v_model/d2v.model')
        results = []
        for page_id in model.docvecs.most_similar(
                positive={object_id, }):
            if page_id[1] > 0.7:
                results.append(page_id[0])
        return results

    def _format_for_train(self, text):
        text = re.sub(r"\n", "", text)
        text = re.sub(r"\s", "", text)
        return text
