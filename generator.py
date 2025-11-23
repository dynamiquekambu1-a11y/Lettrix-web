import os
import random
import re

# Base path pour les dossiers de textes
BASE_PATH = r"C:\lettrix"  # À adapter selon ton arborescence

def lire_paragraphes(path):
    """Lit tous les paragraphes d'un fichier texte séparés par des lignes vides."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        contenu = f.read().strip()
    paragraphes = [p.strip() for p in contenu.split("\n\n") if p.strip()]
    return paragraphes

def accorder_genre(texte, genre):
    """
    Ajuste automatiquement le texte selon le genre choisi.
    Gère les suffixes comme (e), (se), (ve), (trice), etc.
    """
    if genre == "f":
        texte = re.sub(r"\(e\)", "e", texte)
        texte = re.sub(r"\(se\)", "se", texte)
        texte = re.sub(r"\(ve\)", "ve", texte)
        texte = re.sub(r"\(trice\)", "trice", texte)
        texte = re.sub(r"\b(le|un)\b", lambda m: "la" if m.group(1) == "le" else "une", texte)
    else:
        texte = re.sub(r"\([^)]*\)", "", texte)
        texte = re.sub(r"\b(la|une)\b", lambda m: "le" if m.group(1) == "la" else "un", texte)
    texte = re.sub(r"\s+", " ", texte)
    return texte.strip()

def generer_lettre(categorie, style, champs, fichiers=None, nb_paragraphes=(1, 3)):
    """
    Génère une lettre complète avec Introduction / Corps / Conclusion.
    """

    # 🔥 Protection si l'utilisateur n'a pas choisi catégorie ou style
    if not categorie or not style:
        return "⚠️ Veuillez sélectionner une catégorie et un style avant de générer la lettre."

    if fichiers is None:
        fichiers = ["intro.txt", "corps.txt", "conclusion.txt"]

    sections = {}
    for nom_fichier in fichiers:
        path = os.path.join(BASE_PATH, categorie, style, nom_fichier)
        paragraphes = lire_paragraphes(path)
        if paragraphes:
            nb = random.randint(*nb_paragraphes)
            choisis = random.sample(paragraphes, min(nb, len(paragraphes)))
            key = os.path.splitext(nom_fichier)[0]  # "intro", "corps", "conclusion"
            sections[key] = "\n\n".join(choisis)
        else:
            sections[key] = ""

    # Remplacement des balises
    for sec_name, texte in sections.items():
        for key, val in champs.items():
            texte = texte.replace(f"{{{{{key}}}}}", val)
        sections[sec_name] = accorder_genre(texte, champs.get("genre", "m"))

    texte_final = "\n\n".join([
        sections.get("intro", ""),
        sections.get("corps", ""),
        sections.get("conclusion", "")
    ]).strip()

    return texte_final
