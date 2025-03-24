import pdfplumber
import re

def assign_values(target, numbers, keys=("TAC", "NET", "%", "P.M.")):
    """
    Affecte dans le dictionnaire target les nombres en associant chaque valeur
    aux clés données dans keys (par défaut : TAC, NET, %, P.M.).
    """
    for key, number in zip(keys, numbers):
        target[key] = number

def process_total_line(ligne, resultats, regex_nombres):
    """
    Traite une ligne commençant par TOTAL.
      - Si "Kiosk" est présent, affecte la ligne dans "TOTAL Kiosk".
      - Si la ligne contient exactement 9 nombres, on considère qu'il s'agit
        du tableau des produits et on extrait la première valeur dans "TOTAL PRODUITS NET".
      - Sinon, c'est le TOTAL générique.
    """
    nombres = re.findall(regex_nombres, ligne)
    print(f"TOTAL candidate -> {nombres}")
    
    if "Kiosk" in ligne:
        if not resultats["TOTAL Kiosk"] and len(nombres) >= 4:
            assign_values(resultats["TOTAL Kiosk"], nombres)
    elif len(nombres) == 9:
        if not resultats["TOTAL PRODUITS NET"]:
            resultats["TOTAL PRODUITS NET"]["PRODUITS_NET_ALIMENTAIRES"] = nombres[0]
    else:
        if not resultats["TOTAL"] and len(nombres) >= 4:
            assign_values(resultats["TOTAL"], nombres)

def process_normal_line(ligne, categories_normales, resultats, regex_nombres):
    """
    Parcourt les motifs pour les catégories normales (non-TOTAL).
    Si une correspondance est trouvée et que la catégorie n'est pas déjà remplie,
    on affecte les 4 premières valeurs numériques (TAC, NET, %, P.M.).
    """
    for pattern, label in categories_normales.items():
        if re.search(pattern, ligne.strip(), flags=re.IGNORECASE):
            if not resultats[label]:
                nombres = re.findall(regex_nombres, ligne)
                print(f"Trouvé : {label} -> {nombres}")
                if len(nombres) >= 4:
                    assign_values(resultats[label], nombres)
            break

def extraire_donnees_surlignees(pdf_path):
    """
    Extrait les données pour :
      - Kiosk sur place, Kiosk à emporter, McDrive, Sur place, A emporter
      - TOTAL, TOTAL Kiosk et TOTAL PRODUITS NET
      - La date, lorsque celle-ci apparaît après "Feuille de caisse" au format "Mois Année" (ex. "Décembre 2024")
      
    Pour TOTAL PRODUITS NET, on suppose que la ligne contient 9 nombres.
    Les autres lignes fournissent 4 nombres (TAC, NET, %, P.M.).
    """
    # Catégories non-TOTAL
    categories_normales = {
        r"^Sur place": "Sur place",
        r"^A emporter": "A emporter",
        r"^McDrive": "McDrive",
        r"^Kiosk sur place": "Kiosk sur place",
        r"^Kiosk à emporter": "Kiosk à emporter",
    }
    
    resultats = {
        "Date": None,
        "Sur place": {},
        "A emporter": {},
        "McDrive": {},
        "TOTAL": {},
        "Kiosk sur place": {},
        "Kiosk à emporter": {},
        "TOTAL Kiosk": {},
        "TOTAL PRODUITS NET": {}
    }
    
    regex_nombres = r'\d+(?:[\.,]\d+)?'
    # Regex pour extraire une date au format "Mois Année" en français (ex: Décembre 2024)
    regex_date_moyear = r'\b(?:janvier|février|mars|avril|mai|juin|juillet|ao[uû]t|septembre|octobre|novembre|d[eé]cembre)\s+\d{4}\b'
    feuille_de_caisse_detectee = False

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            texte = page.extract_text() or ""
            lignes = texte.split('\n')
            
            for ligne in lignes:
                print(f"Ligne : {ligne}")
                # Extraction de la date après "Feuille de caisse"
                if feuille_de_caisse_detectee and resultats["Date"] is None:
                    match_date = re.search(regex_date_moyear, ligne, flags=re.IGNORECASE)
                    if match_date:
                        resultats["Date"] = match_date.group()
                        print(f"Date trouvée : {resultats['Date']}")
                        feuille_de_caisse_detectee = False
                        
                if "Feuille de caisse" in ligne:
                    feuille_de_caisse_detectee = True

                # Traitement des lignes TOTAL
                if ligne.strip().upper().startswith("TOTAL"):
                    process_total_line(ligne, resultats, regex_nombres)
                    continue  # Passe à la ligne suivante
                    
                # Traitement des autres catégories
                process_normal_line(ligne, categories_normales, resultats, regex_nombres)
    
    return resultats

if __name__ == "__main__":
    pdf_path = "sample.pdf"
    donnees = extraire_donnees_surlignees(pdf_path)
    
    for cat, vals in donnees.items():
        print(f"--- {cat} ---")
        print(vals)
