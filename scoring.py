"""Logique de score de Talent Engine (fonctions pures : ni Flask, ni base de données)."""
import unicodedata
from datetime import date, timedelta
from urllib.parse import urlparse

POINTS_COMPETENCES = {
    "javascript": 8,
    "python": 8,
    "html_css": 6,
    "php": 6,
    "sql": 6,
    "git": 6,
}  # total : 40

MOTS_CLES = ["apprendre", "projet", "equipe", "contribuer", "skullvi", "stage", "evoluer", "passion"]

SEUIL_PRIORITE = 70
SEUIL_ETUDIER = 40


def _normaliser(texte):
    """Minuscules et sans accents, pour comparer les mots-clés."""
    texte = unicodedata.normalize("NFD", texte.lower())
    return "".join(c for c in texte if unicodedata.category(c) != "Mn")


def score_competences(competences):
    # set() évite de compter deux fois la même compétence ; les inconnues valent 0
    return sum(POINTS_COMPETENCES.get(c, 0) for c in set(competences or []))


def score_experience(annees):
    if annees >= 2:
        return 25
    if annees == 1:
        return 15
    return 5


def score_motivation(texte):
    texte = (texte or "").strip()
    longueur = 10 if len(texte) >= 300 else 5 if len(texte) >= 150 else 0
    normalise = _normaliser(texte)
    trouves = sum(1 for mot in MOTS_CLES if mot in normalise)
    return longueur + min(trouves * 2, 10)


def _en_date(valeur):
    if isinstance(valeur, date):
        return valeur
    try:
        return date.fromisoformat(str(valeur))
    except ValueError:
        return None


def score_disponibilite(disponibilite, aujourd_hui=None):
    aujourd_hui = aujourd_hui or date.today()
    d = _en_date(disponibilite)
    if d is None:
        return 0
    if d <= aujourd_hui:
        return 10
    if d <= aujourd_hui + timedelta(days=30):
        return 5
    return 0


def score_lien(lien):
    url = urlparse((lien or "").strip())
    return 5 if url.scheme in ("http", "https") and url.netloc else 0


def calculer_detail(candidat, aujourd_hui=None):
    """Retourne le détail du score par critère (utile pour l'afficher et l'expliquer)."""
    return {
        "competences": score_competences(candidat.get("competences")),
        "experience": score_experience(candidat.get("experience", 0)),
        "motivation": score_motivation(candidat.get("motivation")),
        "disponibilite": score_disponibilite(candidat.get("disponibilite"), aujourd_hui),
        "lien": score_lien(candidat.get("lien")),
    }


def calculer_score(candidat, aujourd_hui=None):
    return sum(calculer_detail(candidat, aujourd_hui).values())


def categorie(score):
    if score >= SEUIL_PRIORITE:
        return "À examiner en priorité"
    if score >= SEUIL_ETUDIER:
        return "À étudier"
    return "Faible adéquation"
