# Auteur: Mica Ménard Human2Chatbot (2018)
# Filtrage : négatif
# Mots déclencheurs : union
# Priorité des règles : longueur inverse

import glob
import pandas as pd
import argparse, sys
import csv
import pickle
import re
import pickle
import enchant
from subprocess import Popen, PIPE
from string import punctuation
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk import TweetTokenizer

#############
# Fonctions #
#############

# élimine les "stop words"
stop_words = stopwords.words('english') + list(punctuation) + ['nt', 's'] # + remove stuff like n't, 's, ...

#identifie si une chaîne de caractères est alphanumérique
def is_alpha(string):
    regex = re.compile('[^a-zA-Z]')
    return bool(regex.sub('', string))

#identifie si une chaîne de caractères est une URL
def is_url(string):
    return bool(re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', string))

#"Tokenise" une chaîne de caractères
def tokenize(text):
    words = word_tokenize(text)
    words = [re.sub('[\']', '', w.lower()) for w in words]
    return [w for w in words if w not in stop_words and not w.isdigit() and is_alpha(w) and not is_url(w)]

#Génère des mots-clés par filtrage négatif d'un dictionnaire général
def keywords(string):
    dictionary = enchant.Dict("en_US")
    kwords = tokenize(string)
    return [keyword for keyword in kwords if not dictionary.check(keyword)]

##############
# Paramètres #
##############

parser=argparse.ArgumentParser()
parser.add_argument('--file', help="If true, rules are built from single file, otherwise from directory", action="store_true")
parser.add_argument('--topic', help="Topic to build rules from")
parser.add_argument('--source', help="Target file (csv) or directory")
args=parser.parse_args()

topic, source = str(args.topic), str(args.source)

#Si fichier unique
if args.file:
    #crée un sous-corpus autour du thème
    def topic_corpus():
        with open(source, newline='', encoding='utf_8') as f:
            reader = csv.reader(f)
            return list(reader)
#Sinon, on sélectionne les fichiers d'un dossier
else:
    def topic_corpus():
        pipe = Popen("grep -rl "+source+" -e "+topic, shell=True,  stdout=PIPE)
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
    triggers = set(sum([keywords for keywords, rule in rules], [])) #flattens the list and turns it into a set
    triggers = [t for t in triggers if t.isalnum()]
    file_content = "TOPIC: ~"+topic+" repeat keep ["+" ".join(triggers)+"]\n\n"
    for keywords, rule in rules:
        file_content += rule+'\n\n'
    return file_content

########
# Main #
########

if __name__ == '__main__':
    couples = couples()
    rules = [[keywords(couple[0]),build_rule(couple)] for couple in couples[:1000] if build_rule(couple)]
    rules.sort(key=lambda item: (-len(item[0]), item[0]))
    topic_content = build_topic(rules)
    with open(topic+".top", "w") as topic_file:
        topic_file.write(topic_content)
        print("Fichier thème créé.")
