""" from pdfquery import PDFQuery

pdf = PDFQuery("sample.pdf")
pdf.load()

label = pdf.pq('LTTextLineHorizontal')

text = [t.text for t in label]

print(text+['\n']) """
""" import PyPDF2

with open('sample.pdf', 'rb') as pdf_file:
    reader = PyPDF2.PdfReader(pdf_file)

    # Get the total number of pages
    total_pages = len(reader.pages)
    print(f"Total pages: {total_pages}")

    # Read the content of the first page
    first_page = reader.pages[0]
    text = first_page.extract_text()
    print(text)
 """

""" import pdfplumber
import pandas as pd

def extract(path):
    total_tables = []

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                df = pd.DataFrame(table)
                total_tables.append(df)
    return total_tables

path = "sample.pdf"
tables = extract(path)
for i, table in enumerate(tables):
    print(f"\n📌 Tableau {i+1}:")
    print(table)

    # Optionnel : Exporter en CSV
    table.to_csv(f"tableau_{i+1}.csv", index=False) """

""" import pdfplumber
import pandas as pd

def extract_first_table(pdf_path):

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            
            if tables:
                df = pd.DataFrame(tables[1])

                # 📌 Suppression des colonnes contenant plus de 80% de None
                df = df.dropna(axis=1, thresh=len(df) * 0.2)  # Supprime les colonnes presque vides

                # 📌 Suppression des lignes totalement vides
                df = df.dropna(axis=0, how="all")

                # 📌 Suppression des espaces vides dans les cellules
                df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

                # 📌 Vérifier la structure du tableau après nettoyage
                print(f"\n📊 Tableau après suppression des colonnes inutiles :\n{df.head()}")

                # 📌 Si la première ligne contient des noms de colonnes, l'utiliser
                if all(isinstance(x, str) and len(x) > 0 for x in df.iloc[0]):
                    df.columns = df.iloc[0]  # Prendre la première ligne comme en-têtes
                    df = df[1:].reset_index(drop=True)  # Supprimer la première ligne utilisée comme colonnes

                # 📌 Vérification du nombre de colonnes après réorganisation
                print(f"\n✅ Nombre de colonnes après nettoyage : {len(df.columns)}")

                # 📌 Essayer de détecter automatiquement les colonnes utiles
                expected_columns = ["Catégorie", "TAC", "NET", "%", "P.M."]
                df.columns = expected_columns[:len(df.columns)]  # Adapter dynamiquement

                # 📌 Conversion automatique des valeurs numériques
                for col in ["TAC", "NET", "P.M."]:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')

                # 📌 Vérification finale du tableau propre
                print(f"\n📊 Tableau final propre :\n{df.head()}")

                return df

    return None

def extract_specific_values(df):

    try:
        print("\n✅ Colonnes détectées :", df.columns.tolist())  # Vérification des colonnes

        # Vérifier si "Catégorie" existe bien
        if "Catégorie" in df.columns:
            net_total = df[df["Catégorie"].str.contains("TOTAL", na=False)]["NET"].values[0]
            pm_kiosk_emporter = df[df["Catégorie"].str.contains("Kiosk à emporter", na=False)]["P.M."].values[0]
        else:
            raise KeyError("La colonne 'Catégorie' n'a pas été détectée correctement.")

        print(f"\n📌 Valeur NET de TOTAL : {net_total}")
        print(f"📌 Valeur P.M. de Kiosk à emporter : {pm_kiosk_emporter}")

        return {
            "NET_TOTAL": net_total,
            "PM_KIOSK_A_EMPORTER": pm_kiosk_emporter
        }
    except IndexError:
        print("\n⚠️ Impossible de trouver certaines valeurs spécifiques.")
        return {}

# 📌 Chemin du fichier PDF
pdf_path = "sample.pdf"

# 📌 Extraction du tableau
df_table = extract_first_table(pdf_path)

if df_table is not None:
    print("\n✅ Premier tableau extrait avec succès !")

    # 📌 Extraire les valeurs spécifiques
    specific_values = extract_specific_values(df_table)

    # 📌 Sauvegarde des valeurs spécifiques
    df_values = pd.DataFrame([specific_values])
    df_values.to_csv("valeurs_specifiques.csv", index=False)
    print("\n✅ Fichier CSV enregistré : valeurs_specifiques.csv")
else:
    print("\n❌ Aucun tableau trouvé dans le PDF.")
 """

import pdfplumber
import re
import pandas as pd

def extraire_donnees_tableau(chemin_pdf):
    """
    Extrait les données d'un tableau de PDF en utilisant une approche plus robuste
    combinant l'extraction de texte et le traitement par ligne.
    """
    resultats = {}
    
    with pdfplumber.open(chemin_pdf) as pdf:
        for i, page in enumerate(pdf.pages):
            # Extraire tout le texte de la page
            texte = page.extract_text()
            
            # Diviser le texte en lignes
            lignes = texte.split('\n')
            
            # Parcourir chaque ligne pour trouver les données pertinentes
            for ligne in lignes:
                # Chercher les lignes qui correspondent à nos catégories d'intérêt
                for categorie in ["Sur place", "A emporter", "McDrive", "TOTAL", "McCafé", "Kiosk"]:
                    if categorie in ligne:
                        # Utiliser une expression régulière pour extraire les valeurs numériques
                        pattern = r'(\b[A-Za-zéàèêëï\s\.]+\b)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?\s*%?)\s+(\d+(?:\.\d+)?)'
                        match = re.search(pattern, ligne)
                        
                        if match:
                            cat, tac, net, pourcentage, pm = match.groups()
                            resultats[cat.strip()] = {
                                'TAC': tac,
                                'NET': net,
                                'Pourcentage': pourcentage,
                                'P.M.': pm
                            }
                        else:
                            # Si le pattern ne correspond pas, essayons de découper manuellement
                            parts = re.split(r'\s{2,}', ligne)
                            if len(parts) >= 5:  # Assurez-vous d'avoir suffisamment de parties
                                cat = parts[0].strip()
                                numbers = [p for p in parts[1:] if re.search(r'\d', p)]
                                if len(numbers) >= 4:
                                    resultats[cat] = {
                                        'TAC': numbers[0],
                                        'NET': numbers[1],
                                        'Pourcentage': numbers[2],
                                        'P.M.': numbers[3]
                                    }
    
    return resultats

# Approche alternative qui essaie d'extraire directement des coordonnées
def extraire_par_ocr_simulation(chemin_pdf):
    """
    Cette fonction simule une approche OCR en extrayant le texte
    avec des coordonnées et en reconstruisant le tableau.
    """
    resultats = {}
    
    with pdfplumber.open(chemin_pdf) as pdf:
        for page in pdf.pages:
            # Extraire tous les caractères avec leurs coordonnées
            words = page.extract_words()
            
            # Regrouper par ligne (y-coordinate)
            lignes = {}
            for word in words:
                y = round(word['top'])  # Arrondir pour regrouper les mots de la même ligne
                if y not in lignes:
                    lignes[y] = []
                lignes[y].append(word)
            
            # Trier chaque ligne par position x
            for y in lignes:
                lignes[y] = sorted(lignes[y], key=lambda w: w['x0'])
            
            # Parcourir les lignes pour trouver les catégories d'intérêt
            for y, mots in sorted(lignes.items()):
                ligne_texte = ' '.join(word['text'] for word in mots)
                
                # Chercher les catégories
                for categorie in ["Sur place", "A emporter", "McDrive", "TOTAL", "McCafé", "Kiosk"]:
                    if categorie in ligne_texte:
                        # Si nous avons au moins 5 mots (catégorie + 4 valeurs)
                        if len(mots) >= 5:
                            cat = mots[0]['text']
                            # Essayer d'extraire les valeurs numériques
                            valeurs = [mot['text'] for mot in mots[1:] if re.search(r'\d', mot['text'])]
                            if len(valeurs) >= 4:
                                resultats[cat] = {
                                    'TAC': valeurs[0],
                                    'NET': valeurs[1],
                                    'Pourcentage': valeurs[2],
                                    'P.M.': valeurs[3]
                                }
    
    return resultats

# Utilisation
if __name__ == "__main__":
    # Essayer les deux approches
    print("=== Approche 1 ===")
    resultats1 = extraire_donnees_tableau("sample.pdf")
    print(resultats1)
    print("\n Test 1 : ", resultats1["Sur place"])
    print("\n Test 2 : ", resultats1["Sur place"]["TAC"])

    print("\n=== Approche 2 ===")
    resultats2 = extraire_par_ocr_simulation("sample.pdf")
    print(resultats2)
    
    # Si vous avez le tableau sous forme d'image plutôt que de PDF
    # Vous pourriez utiliser pytesseract pour l'OCR
    """
    import pytesseract
    from PIL import Image
    
    img = Image.open("tableau.png")
    texte = pytesseract.image_to_string(img, lang='fra')
    lignes = texte.split('\n')
    # ... traiter les lignes comme dans la première fonction
    """