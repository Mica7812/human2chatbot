# Human2Chatbot

Ce dépôt comprend le code utilisé dans l'expérience TER Human2Chatbot (voir article.pdf). Les différents scripts permettent de générer automatiquement des règles [ChatScript](https://github.com/bwilcox-1234/ChatScript) autour d'un thème précis (par exemple *nvidia*) à partir du [corpus Ubuntu](http://dataset.cs.mcgill.ca/ubuntu-corpus-1.0/).

## Prérequis

* Python 3 et librairies :
  * pandas
  * pyenchant
  * nltk
  * gensim

Installation :

```
pip3 install pandas pyenchant nltk
```
Instructions dans les sections suivantes :
* Chatscript
* Corpus Ubuntu

## Étape 1 : Télécharger et installer ChatScript

Pour installer ChatScript il faut préalablement télécharger le dépot github.

```
git clone https://github.com/bwilcox-1234/ChatScript
```

Les instructions d'installation sont disponibles sur [la page github dédiée](https://github.com/bwilcox-1234/ChatScript/blob/master/WIKI/Installing-and-Updating-ChatScript.md).

## Étape 2 : Télécharger le corpus Ubuntu

Le corpus Ubuntu est publiquement disponible [ici](http://dataset.cs.mcgill.ca/ubuntu-corpus-1.0/).

## Étape 3 : Générer des règles

Pour générer des règles ChatScript, suivre la procédure suivante :

```
git clone https://github.com/Mica7812/human2chatbot
cd human2chabot/src/
```

### Prototypes 1, 3 et 4

Pour générer des règles avec les prototypes 1, 3 et 4, il suffit d'exécuter la commande suivante :

```
python3 fichier_du_prototype.py thème dossier_du_corpus_ubuntu
```

Le thème est un mot uniquement à choisir (par exemple : *nvidia*)

### Prototype 2

Pour générer des règles avec le prototype 2, il suffit d'exécuter la commande suivante :

```
python3 prototype2.py --topic=thème --source=dossier_du_corpus_ubuntu
```

La source peut être soit un dossier ou un fichier unique de type csv ou tsv (dans ce cas, fournir le paramètre `--file=True`).


## Étape 4 : Tester le chatbot

Une fois les fichiers `*.top` (thèmes) créés, il suffit de créer un chatbot ChatScript afin de pouvoir les tester. [Cette ressource](https://medium.freecodecamp.org/chatscript-for-beginners-chatbots-developers-c58bb591da8) fournit les informations nécessaire pour y procéder.

Le chatbot ainsi créé, il faut ensuite ajouter le(s) fichier(s) `*.top` dans le dossier `RAWDATA/NOM_DU_BOT` du dossier d'installation ChatScript.

Enfin, après l'exécution du chatbot, il suffit d'exécuter la commande suivante pour compiler celui-ci avec les nouvelles règles :

```
:build nom_du_bot
```
