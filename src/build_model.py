# Auteur: Mica Ménard Human2Chatbot (2018)
# Script conçu pour la création d'un modèle tf-idf sur le corpus Ubuntu

from gensim.models import TfidfModel
from gensim.corpora import Dictionary
from nltk import word_tokenize
import csv
import random
import sys
import glob
import pandas as pd

#Chemin vers le dossier d'entraînement du modèle
path = str(sys.argv[1])

def build_dict_model(path):
    allFiles = glob.glob(path + "/*.tsv")
    _list = [pd.read_csv(f,header = None, delimiter="\t", quoting=csv.QUOTE_NONE, encoding='utf-8') for f in allFiles]
    frame = pd.concat(_list)
    myhash = str(random.getrandbits(8))
    tokens = [word_tokenize(str(row)) for row in frame.ix[:,3]]
    dictionary = Dictionary(tokens)
    dictionary.save("ressources/dictionary"+myhash)
    tfidf_model = TfidfModel([dictionary.doc2bow(t) for t in tokens], id2word=dictionary)
    tfidf_model.save("ressources/tfidf_model"+myhash)

if __name__ == '__main__':
    build_dict_model(path)
    print("Modèle tf-idf créé.")
