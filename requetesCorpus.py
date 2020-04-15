# encoding: utf-8
import collections
import indexreq
import sys



#################### FONCTIONS###########################

def filter_keywords(keywords):
        """
       Les opérateurs +,-, 0 sont la base de la répartition des mots de la requête en listes séparées. 
        Arguments:
            La liste des mots-clés
        Renvoie:
            La liste des mots-clés sans les opérateurs
            Le dictionnaire avec les mots-clés: clé : un des opérateurs, valeur : liste des mots de la requête correspondants à cet opérateur
        """
       
        keywords_gr = {"P":[], "A":[], "O":[]}
        for word in keywords:
            if word.startswith("+"): keywords_gr["P"].append(word[1:])
            elif word.startswith("-"): keywords_gr["A"].append(word[1:])
            else: keywords_gr["O"].append(word)
        
        keywords_clean = [kw for lkw in keywords_gr.values() for kw in lkw]
        return keywords_clean, keywords_gr
    
    
    
def get_documents(keywords_gr, index):
        """
        Cette fonction retourne les documents qui ont les mots de la requête(+,-,0)
        Arguments:
            Le dictionnaire avec les mots-clés
        Renvoie:
           Le dictionnaire contenant les documents retrouvés, les clés: ids des documents, les valeurs : fréquences associées
        """
        
        extract_docs = {}
        for word in keywords_gr["P"] + keywords_gr["O"]+keywords_gr["A"]:
           # for doc_id, freq in index[word].items():
                #print(index)
                for n in range(0,int(len(index[word]))):
                    doc_id=index[word][n][0]
                    freq=index[word][n][1]
                    doc = extract_docs.setdefault(doc_id, {})
                    doc.update({word:freq})

        return extract_docs
        
    
    
def trie_documents(docs_extraits, motcles_gr):
    """
    Cette fonction retourne la liste des documents qui ont les mots clés obligatoires et non obligatoires et n'nont pas de mots interdits
    
    Arguments: 
        Le dictionnaire contenant les documents retrouvés, les clés: ids des documents, les valeurs : fréquences associées
        Le dictionnaire avec les mots-clés: clé : un des opérateurs, valeur : liste des mots de la requête correspondants à cet opérateur
    Renvoie:
        le dictionnaire où la clé est l'id du document trouvés et la valeur est un dictionnaires avec clés: mot de la requête, valeur: sa fréquance dans le document. 
    """
    liste_finale=dict()
    result_non_trie=dict()
    for k in docs_extraits.keys():
        listee=[]
        mots=k
        for t in motcles_gr["P"]:
            if t in docs_extraits[mots].keys():
                listee.append(True)
            else:
              listee.append(False)
        if all(listee):
            liste_finale[mots]=docs_extraits[mots]
    
    
    for doc in liste_finale.keys():
        listee=[]
        mot=doc
        for m in motcles_gr["A"]:
            if m in liste_finale[mot].keys():
                listee.append(False)
            else:
                listee.append(True)
        if all(listee):
            result_non_trie[doc]=liste_finale[mot]
    
    return result_non_trie



def dict_id_freq(result_non_trie):
    """
    La fonction compte la fréquence de la totalité des termes demandés pour chaque document
    
    Arguments: 
        le dictionnaire où la clé est l'id du document trouvés et la valeur est un dictionnaires avec clés: mot de la requête, valeur: sa fréquance dans le document. 
        
    Renvoie:
        Dicttionnaire. clé : id du document. Valeur: la fréquence totale de ces termes
    """
    dictid_freq=dict()
    for kk in result_non_trie.keys():
        freq=0
        keycontents=result_non_trie[kk]
        for word in keycontents.keys():
            
            freq=keycontents[word]+freq
            
        dictid_freq[kk]=freq
    return dictid_freq




def evalpertinence(idFreq):
    """
    Cette fonction trie les documents par pértinence(le critère est la fréquence absolut des termes)
    
    Arguments:
        Dictionnaire. clé : id du document. Valeur: la fréquence totale de ces termes
        
    Renvoie:
        Liste à deux dimentions avec les documents par ordre décroissante en fonction de leur score: premier 1 colonne: id des docs. 2 colonne: leur score
    """
    listeParPertinence=[]
    maximum=0
    dictFreq=idFreq
    for k, v in sorted(idFreq.items(), key=lambda x: x[1], reverse=True):
        listeParPertinence.append([k,v])
        
    return listeParPertinence



def getdocs(docs, pert, ind, score):
    """
    Imprime les documents pertinents sur la sortie standard
    
    Arguments:
        indexe des documents
        la liste avec les documents pertinents
        index 
        score
        
    Renvoie:
        String avec le document pertinene, son titre et son score et le rang
    """
    
    for k in docs.keys():
        kk=int(k)
        if pert == kk:
            res=docs[k]
            #écriture dans le log
            with open ("log.txt", 'a') as logg:
                logg.write("titre du document: {}\nindex calculé: {}\n".format(res[1], score))
            return "Le rang est {}\nLe score est {}\nLe titre est : {}\n ".format(ind, score, res[1])
 



############################## MAIN ####################################

"""
Ce programme fait les requêtes sur le corpus des documents indexés. 
"""
req=input("Tapez les requêtes en les séparant par un espace: ")
#écrire dans le log début exécution
with open ("log.txt", 'w') as loggi:
                loggi.write("Le programme est en cours d'exécution\n")

#boucle qui permet de faire plusieurs requêtes. Mot de sortie est STOPPROG
while req!="STOPPROG":
    with open ("log.txt", 'a') as logi:
                logi.write("\nNouvelle requête\nTermes: {}\n".format(req))
    #traitement des requêtes. création de la liste et désaccentuation
    req=req.split()
    req=" ".join(indexreq.desaccentueLesTokens(req)).lower()
    req=req.split()

    #répartition des mots de la requête en listes séparés
    mots_cles, motcles_gr=filter_keywords(req)


    #lecture index  inversé et index docs
    termes = indexreq.lireDansUnFichier("IndexTermes.json")
    docs=indexreq.lireDansUnFichier("IndexDocs.json")


    #les documents qui ont les mots de la requête(+,-,0)
    docs_extraits=get_documents(motcles_gr, termes)


    #documents qui ont les mots clés obligatoires et non obligatoires et n'nont pas de mots interdits
    res_trie=trie_documents(docs_extraits, motcles_gr)


    #compte la fréquence de la totalité des termes demandés pour chaque document
    idFreq=dict_id_freq(res_trie)


    #trie les documents par pértinence
    docs_pert=evalpertinence(idFreq)

    # affichage des résultats
    print("Le nombre de docs trouvés est ", len(docs_pert))
    
    for d in docs_pert:
        ind=docs_pert.index(d)+1
        pert=d[0]
        score=d[1]
 
        print(getdocs(docs, pert, ind, score))
    req=input("Tapez les requêtes en les séparant par un espace: ")

with open ("log.txt", 'a') as logii:
                logii.write("Le programme est arrêté")

