import os
import random
import re

# 📌 Localisation automatique du dossier "lettres"
BASE_PATH = os.path.join(os.path.dirname(__file__), "lettres")

def lire_paragraphes(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        contenu = f.read().strip()
    return [p.strip() for p in contenu.split("\n\n") if p.strip()]

def accorder_genre(texte, genre):
    if genre == "f":
        texte = re.sub(r"\(e\)", "e", texte)
        texte = re.sub(r"\(se\)", "se", texte)
        texte = re.sub(r"\(ve\)", "ve", texte)
        texte = re.sub(r"\(trice\)", "trice", texte)
        texte = re.sub(r"\b(le|un)\b", lambda m: "la" if m.group(1) == "le" else "une", texte)
    else:
        texte = re.sub(r"\([^)]*\)", "", texte)
        texte = re.sub(r"\b(la|une)\b", lambda m: "le" if m.group(1) == "la" else "un", texte)

    return re.sub(r"\s+", " ", texte).strip()

def generer_lettre(categorie, style, champs, fichiers=None, nb_paragraphes=(1, 3)):
    if not categorie or not style:
        return "⚠️ Veuillez sélectionner une catégorie et un style avant de générer la lettre."

    if fichiers is None:
        fichiers = ["intro.txt", "corps.txt", "conclusion.txt"]

    sections = {}

    for nom_fichier in fichiers:
        key = os.path.splitext(nom_fichier)[0]
        path = os.path.join(BASE_PATH, categorie, style, nom_fichier)

        paragraphes = lire_paragraphes(path)

        if paragraphes:
            nb = random.randint(*nb_paragraphes)
            choisis = random.sample(paragraphes, min(nb, len(paragraphes)))
            sections[key] = "\n\n".join(choisis)
        else:
            sections[key] = ""

    for sec_name, texte in sections.items():
        for key, val in champs.items():
            texte = texte.replace(f"{{{{{key}}}}}", val)
        sections[sec_name] = accorder_genre(texte, champs.get("genre", "m"))

    return ("\n\n".join([
        sections.get("intro", ""),
        sections.get("corps", ""),
        sections.get("conclusion", "")
    ])).strip()
