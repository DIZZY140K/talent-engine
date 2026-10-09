"""Validation des champs du formulaire (côté serveur : on ne fait jamais confiance au navigateur)."""
import re
from datetime import date
from urllib.parse import urlparse

from scoring import POINTS_COMPETENCES

NIVEAUX = ["bac", "bac+1", "bac+2", "bac+3", "bac+4", "bac+5"]
REGEX_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def valider(form):
    """Reçoit un dictionnaire (competences = liste) et retourne (donnees, erreurs).

    - donnees : valeurs nettoyées, prêtes pour scoring.py et la base
    - erreurs : dictionnaire {champ: message}, vide si tout est valide
    """
    erreurs = {}
    donnees = {}

    nom = str(form.get("nom") or "").strip()
    if not 2 <= len(nom) <= 100:
        erreurs["nom"] = "Entrez votre nom (2 à 100 caractères)."
    donnees["nom"] = nom

    email = str(form.get("email") or "").strip().lower()
    if len(email) > 254 or not REGEX_EMAIL.match(email):
        erreurs["email"] = "Entrez une adresse email valide."
    donnees["email"] = email

    niveau = str(form.get("niveau") or "").strip()
    if niveau not in NIVEAUX:
        erreurs["niveau"] = "Choisissez un niveau d'études."
    donnees["niveau"] = niveau

    try:
        experience = int(str(form.get("experience", "")).strip())
        if not 0 <= experience <= 50:
            raise ValueError
    except ValueError:
        experience = 0
        erreurs["experience"] = "Entrez un nombre entier entre 0 et 50."
    donnees["experience"] = experience

    competences = form.get("competences") or []
    if isinstance(competences, str):
        competences = [competences]
    if any(c not in POINTS_COMPETENCES for c in competences):
        erreurs["competences"] = "Une des compétences envoyées n'existe pas."
    donnees["competences"] = sorted(set(c for c in competences if c in POINTS_COMPETENCES))

    brut = str(form.get("disponibilite") or "").strip()
    try:
        donnees["disponibilite"] = date.fromisoformat(brut)
    except ValueError:
        donnees["disponibilite"] = None
        erreurs["disponibilite"] = "Choisissez une date valide."

    lien = str(form.get("lien") or "").strip()
    if lien:
        url = urlparse(lien)
        if url.scheme not in ("http", "https") or not url.netloc:
            erreurs["lien"] = "Le lien doit commencer par http:// ou https://."
    donnees["lien"] = lien

    motivation = str(form.get("motivation") or "").strip()
    if not 50 <= len(motivation) <= 2000:
        erreurs["motivation"] = "Écrivez entre 50 et 2000 caractères."
    donnees["motivation"] = motivation

    return donnees, erreurs
