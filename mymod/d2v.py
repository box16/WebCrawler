from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from .db_access import DBAccess
from .nlp import NLP
import re
import os
from smart_open import open


class Corpus:
    def __init__(self):
        self.corpus_path = "/home/pi/My_App/Web_Scrap_for_Python/corpus.txt"
        self._nlp = NLP()
        documents = DBAccess().get_all_pages_data()
        with open(self.corpus_path, "w") as f:
            for object_id, body in documents:
                body = self._format_for_train(body)
                f.write(body + "," + str(object_id) + "\n")

    def _format_for_train(self, text):
        text = re.sub(r"\n", "", text)
        text = re.sub(r"\s", "", text)
        text = re.sub(r",", "", text)
        return text

    def __iter__(self):
        for line in open(self.corpus_path):
            document = line.split(",")
            words = self._nlp.analyze_morphological(document[0])
            yield TaggedDocument(words=words, tags=[int(document[1])])

    def __del__(self):
        os.remove(self.corpus_path)


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
        model.save(self.model_file)
        model.delete_temporary_training_data(
            keep_doctags_vectors=True, keep_inference=True)

    def find_similer_articles(self, object_id):
        """指定したidに似ているベクトルの他記事を5つピックする"""
        model = Doc2Vec.load(self.model_file)
        return model.docvecs.most_similar(positive={object_id, })
