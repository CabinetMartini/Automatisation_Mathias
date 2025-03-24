import pdfplumber
import re
import pandas as pd

def extraire_donnees_surlignees(pdf_path):
    """
    Extrait les données pour :
      - Kiosk sur place
      - Kiosk à emporter
      - TOTAL Kiosk
      - TOTAL PRODUITS NET
      - Sur place
      - A emporter
      - McDrive
      - TOTAL
      
    Pour TOTAL PRODUITS NET, on suppose que la ligne contient 9 nombres.
    Les autres lignes fournissent 4 nombres (TAC, NET, %, P.M.).
    """
    # Dictionnaire pour les catégories autres que TOTAL
    categories_normales = {
        r"^Sur place": "Sur place",
        r"^A emporter": "A emporter",
        r"^McDrive": "McDrive",
        r"^Kiosk sur place": "Kiosk sur place",
        r"^Kiosk à emporter": "Kiosk à emporter",
    }
    
    resultats = {
        "Sur place": {},
        "A emporter": {},
        "McDrive": {},
        "TOTAL": {},
        "Kiosk sur place": {},
        "Kiosk à emporter": {},
        "TOTAL Kiosk": {},
        "TOTAL PRODUITS NET": {},
        "Date": None,
        "Nom du fichier": pdf_path
    }
    
    regex_nombres = r'\d+(?:[\.,]\d+)?'
    # Regex pour extraire une date au format dd/mm/yy (exemple : 01/03/25)
    regex_date_moyear = r'\b(?:janvier|février|mars|avril|mai|juin|juillet|ao[uû]t|septembre|octobre|novembre|d[eé]cembre)\s+\d{4}\b'
    feuille_de_caisse_detectee = False

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            texte = page.extract_text() or ""
            lignes = texte.split('\n')
            
            for ligne in lignes:
                #print(f"Ligne : {ligne}")
                # Recherche de la date si "Feuille de caisse" a été détecté sur la ligne précédente
                if feuille_de_caisse_detectee and resultats["Date"] is None:
                    match_date = re.search(regex_date_moyear, ligne, flags=re.IGNORECASE)
                    if match_date:
                        resultats["Date"] = match_date.group()
                        #print(f"Date trouvée : {resultats['Date']}")
                        feuille_de_caisse_detectee = False  # On réinitialise le flag
                        
                # Détection de "Feuille de caisse" pour préparer la lecture de la date sur la ligne suivante
                if "Feuille de caisse" in ligne:
                    feuille_de_caisse_detectee = True


                # D'abord, traiter les lignes TOTAL
                if ligne.strip().upper().startswith("TOTAL"):
                    nombres = re.findall(regex_nombres, ligne)
                    #print(f"TOTAL candidate -> {nombres}")
                    if "Kiosk" in ligne:
                        # Il s'agit d'une ligne TOTAL Kiosk
                        if not resultats["TOTAL Kiosk"]:
                            if len(nombres) >= 4:
                                resultats["TOTAL Kiosk"]["TAC"] = nombres[0]
                                resultats["TOTAL Kiosk"]["NET"] = nombres[1]
                                resultats["TOTAL Kiosk"]["%"] = nombres[2]
                                resultats["TOTAL Kiosk"]["P.M."] = nombres[3]
                    elif len(nombres) == 9:
                        # C'est le tableau des produits (TOTAL PRODUITS NET)
                        if not resultats["TOTAL PRODUITS NET"]:
                            resultats["TOTAL PRODUITS NET"]["TAC"] = nombres[0]
                            # Vous pouvez ajouter les autres colonnes si nécessaire
                    else:
                        # Le TOTAL générique
                        if not resultats["TOTAL"]:
                            if len(nombres) >= 4:
                                resultats["TOTAL"]["TAC"] = nombres[0]
                                resultats["TOTAL"]["NET"] = nombres[1]
                                resultats["TOTAL"]["%"] = nombres[2]
                                resultats["TOTAL"]["P.M."] = nombres[3]
                    continue  # passe à la ligne suivante
                    
                # Pour les autres catégories (non-TOTAL)
                for pattern, label_sortie in categories_normales.items():
                    if re.search(pattern, ligne.strip(), flags=re.IGNORECASE):
                        if resultats[label_sortie]:
                            break
                        nombres = re.findall(regex_nombres, ligne)
                        #print(f"Trouvé : {label_sortie} -> {nombres}")
                        if len(nombres) >= 4:
                            resultats[label_sortie]["TAC"] = nombres[0]
                            resultats[label_sortie]["NET"] = nombres[1]
                            resultats[label_sortie]["%"] = nombres[2]
                            resultats[label_sortie]["P.M."] = nombres[3]
                        break
    return resultats


def sauvegarder_resultats(resultats, nom_fichier="resultats_extraction.csv"):
    """
    Sauvegarde les résultats dans un fichier CSV.
    """
    df = pd.DataFrame.from_dict(resultats,orient='columns')
    df_transposed = df.T
    print(df_transposed)
    df_transposed.index.name = 'Catégorie'
    df_transposed.to_csv(nom_fichier)
    print(f"\nRésultats sauvegardés dans {nom_fichier}")


def sanitize_donnes(donnes: dict) -> dict:
    """
    Sanitize extracted data:
      - Supprime les entrées vides du dictionnaire principal.
      - Dans chaque sous-dictionnaire, supprime les valeurs vides.
      - Retire les clés "NET" et "%" (insensibles à la casse) de chaque sous-dictionnaire.
    """
    sanitized = {}
    for key, subdict in donnes.items():
        # Pour la clé "Date" qui n'est pas un sous-dictionnaire, on la conserve telle quelle
        if key == "Date":
            if subdict:
                sanitized[key] = subdict
            continue
        
        # On s'assure que subdict est non vide
        if not subdict:
            continue

        new_subdict = {}
        for subkey, value in subdict.items():
            # Ignore les valeurs vides
            if not value:
                continue
            # On retire les clés "NET" et "%" (on ignore la casse)
            if subkey.upper() in ("NET", "%"):
                continue
            new_subdict[subkey] = value

        if new_subdict:
            sanitized[key] = new_subdict

    return sanitized

    

if __name__ == "__main__":
    pdf_path = "sample.pdf"
    donnees = extraire_donnees_surlignees(pdf_path)
    donnees = sanitize_donnes(donnees)
    sauvegarder_resultats(donnees)

"""     for cat, vals in donnees.items():
        print(f"--- {cat} ---")
        print(vals)
 """
