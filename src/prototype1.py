# Auteur: Mica Ménard Human2Chatbot (2018)
# Filtrage : positif
# Mots déclencheurs : union
# Priorité des règles : ordre alphabétique

import glob
import pandas as pd
import os, sys
import csv
import pickle
import re
from nltk import TweetTokenizer
from subprocess import Popen, PIPE

# Les arguments du script
topic, directory = str(sys.argv[1]), str(sys.argv[2])

#############
# Fonctions #
#############

# Cette fonction de recueillir tous les dialogues d'un dossier du corpus Ubuntu
# où le mot de la variable topic est présent
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

# Définit les mots-clés par filtrage positif du dictionnaire du domaine
def keywords(couple):
    #Dictionnaire du domaine
    dictionary = pickle.load( open( "ressources/vocab.pkl", "rb" ) )
    tknzr = TweetTokenizer()
    words = tknzr.tokenize(couple[0])
    keywords = []
    for w in words:
        if w in dictionary:
            keywords.append(w)
    if keywords: return keywords

# Crée les règles
def build_rule(couple):
    kwords = keywords(couple)
    if kwords:
        #On échappe tous les caractères listés ci-dessous pour ChatScript
        rule = "u: (<< "+" ".join(kwords)+" >>) "+couple[1].translate(str.maketrans({"-":  r"\-",
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
        return rule
    else: return None

#Crée le fichier thème
def build_topic(rules):
    triggers = set(sum([keywords for keywords, rule in rules], [])) #flattens the list and turns it into a set
    #entête du fichier thème
    file_content = "TOPIC: ~"+topic+" repeat keep ["+" ".join(triggers)+"]\n\n"
    for keywords, rule in sorted(rules):
        file_content += rule+'\n\n'
    return file_content

########
# Main #
########

if __name__ == '__main__':
    couples = couples()
    rules = [[keywords(couple),build_rule(couple)] for couple in couples if build_rule(couple)]
    topic_content = build_topic(rules)
    with open(topic+".top", "w") as topic_file:
        topic_file.write(topic_content)
        print("Fichier thème créé.")
