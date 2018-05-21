# Auteur: Mica Ménard Human2Chatbot (2018)
# Filtrage : tf-idf
# Mots déclencheurs : max tf-idf
# Priorité des règles : longueur inverse

import glob
import pandas as pd
import os, sys
import csv
import pickle
import re
from subprocess import Popen, PIPE
from gensim.models import TfidfModel
from gensim.corpora import Dictionary
from string import punctuation
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk import TweetTokenizer

#############
# Fonctions #
#############

# élimine les "stop words"
stop_words = stopwords.words('english') + list(punctuation) + ['nt', 's'] # + remove stuff like n't, 's, ...
# chargement du dictionnaire et du modèle tf-idf
dictionary = Dictionary.load("ressources/dictionary")
tfidf_model = TfidfModel.load("ressources/tfidf_model")

#identifie si une chaîne de caractères est alphanumérique
def is_alpha(string):
    regex = re.compile('[^a-zA-Z]')
    return bool(regex.sub('', string))

#identifie si une chaîne de caractères est une URL
def tokenize(text):
    words = word_tokenize(text)
    words = [re.sub('[\']', '', w.lower()) for w in words if not re.match('//*/*', w)] # filters urls
    return [w for w in words if w not in stop_words and not w.isdigit() and is_alpha(w)]

#"Tokenise" une chaîne de caractères
def keywords(string):
    tfidf_values = tfidf_model[dictionary.doc2bow(tokenize(string))]
    scores = [f for e,f in tfidf_values]
    if scores:
        mean = sum(scores)/len(scores)
        result = [dictionary[e] for e,f in tfidf_values if f > mean]
        return result

# Génère un score tf-idf
def score(string):
    tfidf_values = tfidf_model[dictionary.doc2bow(tokenize(string))]
    scores = [[dictionary[e],f] for e,f in tfidf_values]
    return scores

#paramètres
topic, directory = str(sys.argv[1]), str(sys.argv[2])

#crée un sous-corpus autour du thème
def topic_corpus():
    pipe = Popen("grep -rl "+directory+" -e "+topic, shell=True,  stdout=PIPE)
    text = pipe.communicate()[0]
    return list(filter(None,text.decode().split('\n')))

# Définit les couples d'énoncés
def couples():
    files = topic_corpus()
    headers = ['Date', 'UserA', 'UserB', 'Message']
    couples = []
    df = (pd.read_csv(f, sep="\t", quoting=csv.QUOTE_NONE, encoding='latin-1', header=None, names=headers) for f in files)
    for x in df:
        x['test'] = x['UserA'].eq(x.shift(-1)['UserB']) & (x['UserB'].eq(x.shift(-1)['UserA']) )
        for i in range(0,x.shape[0]):
            try:
                if x.iloc[i]['test']:
                    couples.append([x.iloc[i]['Message'],x.iloc[i+1]['Message']])
            except:
                pass
    return couples

# Génère les règles
def build_rule(couple):
    kwords = keywords(couple[0])
    if kwords:
        comment = "#! "+couple[0]+"\n"
        kwords = " ".join(kwords)
        kwords = re.sub(r'[`\*\[\]\(\)\=\^]', '', kwords) # these characters cause problems
        rule = "u: (<< "+ kwords + " >>) "+couple[1].translate(str.maketrans({"-":  r"\-",
                                          "]":  r"",
                                          "[":  r"",
                                          "(": r"",
                                          ")": r"",
                                          "^":  r"\^",
                                          "$":  r"\$",
                                          "*":  r"\*",
                                          "@":  r"\@",
                                          ":":  r"\:",
                                          "#":  r"\#"}))
        return comment+rule
    else: return None

# Crée le fichier thème
def build_topic(rules):
    triggers = set([max(score(" ".join(keywords)))[0] for keywords, rule in rules]) #flattens the list and turns it into a set
    print("# of triggers: %s" % len(triggers))
    file_content = "TOPIC: ~"+topic+" repeat keep ["+" ".join(triggers)+"]\n\n"
    for keywords, rule in rules:
        file_content += rule+'\n\n'
    return file_content

########
# Main #
########
if __name__ == '__main__':
    couples = couples()
    rules = [[keywords(couple[0]),build_rule(couple)] for couple in couples[:700] if build_rule(couple)]
    print("# of rules: %s" % len(rules))
    rules.sort(key=lambda item: (-len(item[0]), item[0]))
    topic_content = build_topic(rules)
    with open(topic+".top", "w") as topic_file:
        topic_file.write(topic_content)
        print("Fichier thème créé.")
