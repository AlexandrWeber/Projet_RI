# encoding: utf-8
import json

"""
Ce module regroupe les fonctions utilisées par l'indexeur et par les requêtes
"""

def lireDansUnFichier(fichier):
    """
    Lit le fichier json
    """
    with open(fichier, "r") as json_data:
        data_dict = json.load(json_data)
        return data_dict


def desaccentueLesTokens(lemmes) :
    """
    Enlève des accents et retoune une liste des mots sans accent
    """
    lemmesSansAccent = []
    table = str.maketrans ("àâéèêîïôùûüÿ", "aaeeeiiouuuy")
    for lemme in lemmes :
        lemmesSansAccent.append (lemme.translate(table))
        
    return lemmesSansAccent 

