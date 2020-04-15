# encoding: utf-8
from bs4 import BeautifulSoup
import lxml
import os
from os.path import basename
import sys
import re
import json
from langdetect import detect
from pprint import pprint
import treetaggerwrapper
import collections
import indexreq
import shutil


"""
C'est un indexeur qui prend en entrée un dossier avec les documents à indexer et crée un index inversé (fichier IndexTermes.json) et index des documents (fichier IndexTermes.json).
L'indexeur est incrémental, c'est-à-dire qu'uncun fichier est indexé deux fois et le dictionnaire est mis mis à jours sans perdre les données existantes
Les termes sont normalisés à l'aide de Treetagger et detecteur de langues

IMPORTANT!
Il faut avoir installé treetaggerwrapper pour pouvoir utiliser ce programme

"""


# réqupère le chemin vers le dossier à indexer depuis l'entrée standard
corpusTextes=str(sys.argv[1])


####################### FONCTIONS OUTILS ################################
    
def giveFileName(fi):   
        """
        Récupère le nom du fichier sans .txt
        
        Arguments:
            Fichier
            
        Renvoie:
            nom du fichier (string)
        """
        fileName, fileExtension = os.path.splitext(fi)
        return fileName
    
    
def giveTitel (fiDoc):
    """
    Récupère le titre du document
    
    Arguments:
        fichier .txt
        
    Renvoie:
        texte(string)
    """
    with open(fiDoc,"r") as infile:
        contents = infile.read()
        soup = BeautifulSoup(contents,'lxml')
        titres = soup.find('titre')
        return titres.get_text().split("\n")[0]
    
def givetexte(fiDoc):
    """
    Récupère le texte dans document
    
    Arguments:
        fichier .txt
        
    Renvoie:
        texte(string)
    """
    with open(fiDoc,"r") as infile:
        contents = infile.read()
        soup = BeautifulSoup(contents,'lxml')
        texte = soup.find('texte')
        return texte.get_text()
    
    
def ecrireDansUnFichier(fichier):
    """
    Ecrit dans le fichier json
    
    Arguments:
        texte (string)
        
    """
    with open ("IndexDocs.json", "w") as texte:
        json.dump(fichier, texte, sort_keys=False, indent=4, ensure_ascii=False)
        
        
        
def ecrireFichierTerme(fichier):
    """
    Ecrit dans le fichier json pour index inversé
    
    Arguments:
        texte (string)
        
    """
    with open ("IndexTermes.json", "w") as texte:
        json.dump(fichier, texte, sort_keys=False, indent=4, ensure_ascii=False)
        

def giveKeyMax(fichier):
    """
    Récupère la clé maximale
    
    Arguments:
        fichier json (IndexDocs)
        
    Renvoie:
        valeur maximale(int)
    """
    with open(fichier, "r") as json_data:
        data_dict = json.load(json_data)
       # max_key = int(max(data_dict, key=lambda k: data_dict[k], default=0))
        valeur=0
        for key in data_dict.keys():
            #print(key)
            if int(key)>int(valeur):
               valeur=key
                
    return int(valeur)


    
def taggerTexte(texte):
    """
    Normalise le texte et renvoie les lemmes
    
    Arguments:
        Texte
        
    Renvoie:
        liste des lemmes pertinents
    """
    texxt=texte.split("’")
    tex="'".join(texxt)
    
    
    if detect(tex)=="fr":
        langdet='fr'
    if detect(tex)=='en':
        langdet='en'
    tagger=treetaggerwrapper.TreeTagger(TAGLANG=langdet)
    tags=tagger.tag_text(tex)
    tags2=treetaggerwrapper.make_tags(tags)
    #pprint(tags2)
    empty=[]
    for tag in tags2:
        tagg=tag
        empty.append(tagg)
        #print(empty)
        
    
    grammar=[]
    for element in empty:
        compt=0
        for i in element:
            if compt==1 or compt==2:
                grammar.append(i)
                grammar.append("\t")
            compt+=1
        grammar.append("\n")
    del grammar[-1]
    res="".join(grammar)
    
    
    ress=res.split("\n")
    
    lemmes=[]
    for rrr in ress:
        if len(rrr)==0 or "@" in rrr:
            del ress[ress.index(rrr)] 
    for rr in ress:
      
        match_tag = re.search(r"(.*)\t(.*)\t", rr)

        if "VER" in match_tag.group(1) or "NOM" in match_tag.group(1) or "ABR" in match_tag.group(1) or "ADJ" in match_tag.group(1) :
             lemmes.append(match_tag.group(2).lower())
        elif "VV" in match_tag.group(1) or "NN" in match_tag.group(1) or "NP" in match_tag.group(1) or "JJ" in match_tag.group(1) or "VH" in match_tag.group(1) or "VB" in match_tag.group(1) or "MD" in match_tag.group(1) :
             lemmes.append(match_tag.group(2).lower())
    return lemmes
    
  

def countfreq(dictkey,listeLemmes):
    """
    Compte les occurences des mots dans untexte données.
    
    Argumnts:
        Liste des lemmes
        
    Renvoie:
        dictionnaire clés: terme; valeur: id du doc et la fréquence (liste à deux dimentions
    """
    listvaleur=indexreq.lireDansUnFichier("IndexTermes.json")
    c=collections.Counter(listeLemmes)
    
    for key, value in c.items():
        if key in listvaleur:
            listvaleur[key].append([dictkey,value])
        else:
            listvaleur[key]=[[dictkey,value]]
        
    return listvaleur
 
 
 
 

############ MAIN ###############################  

#créer le répertoir pour les fichiers indexes s'il n'existe pas
os.makedirs("DocumentsIndexes", exist_ok=True)

#création des fichiers IndexDocs.json et IndexTermes.json si elles n'existent pas
if os.path.isfile("IndexDocs.json")==False:
    indexDoc=dict()
    ecrireDansUnFichier(indexDoc)
else:
    print("The json file exists")

if os.path.isfile("IndexTermes.json")==False:
    indexTermes=dict()
    ecrireFichierTerme(indexTermes)
else:
    print("The IndexTermes file exists")


#parcous de chaque fichier dans le dossier
for fi in sorted(os.listdir (corpusTextes)):
    
    # joindre le fichier au chemin
    fiDoc=corpusTextes+fi
    #récupérer le nom du fichier sans .txt
    FileName=giveFileName(fi)
    #récupérer le titre
    Titel=giveTitel(fiDoc)
    #récupérer le texte
    Texte=givetexte(fiDoc)
    
    
    #normaliser le texte
    listeLemmes=taggerTexte(Texte)
    if detect(Texte)=="fr":
        listeLemmes=indexreq.desaccentueLesTokens(listeLemmes)
        #print(listeLemmes)
        
    #lire le fichier IndexDocs.json; récupérer la valeur maximale de la clé(id des docs)
    indexDoc=indexreq.lireDansUnFichier("IndexDocs.json")
    max_key=giveKeyMax("IndexDocs.json")
    
    #vérification si le doc a déjà été indexé
    if [FileName, Titel] not in indexDoc.values():
        
        #ajout de l'id du document et de son titre dans le dictionnaire
        indexDoc[int(max_key+1)]=[FileName, Titel]
        
        #écriture du dictionnaire mis à jours dans le fichier json
        for key, value in indexDoc.items():
            if value==[FileName, Titel]:
                dictkey=key
        ecrireDansUnFichier(indexDoc)
    
        # copie le fichier indexé dans le dossier Documents indexés
        filePath = shutil.copy(fiDoc, 'DocumentsIndexes')
        
        #écriture des termes dans le fichier json
        resultatFinal=countfreq(dictkey,listeLemmes)
        ecrireFichierTerme(resultatFinal)
data_dict=indexreq.lireDansUnFichier("IndexDocs.json")
