import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scoring import calculer_detail, calculer_score, categorie, score_lien, score_motivation

AUJOURDHUI = date(2026, 10, 7)
TEXTE_LONG = "Je veux apprendre, contribuer a un projet en equipe chez SKULLVI. " * 6


def candidat_ideal():
    return {
        "competences": ["javascript", "python", "html_css", "php", "sql", "git"],
        "experience": 3,
        "motivation": TEXTE_LONG + " passion",
        "disponibilite": AUJOURDHUI,
        "lien": "https://github.com/exemple",
    }


def test_candidat_ideal_obtient_100():
    assert calculer_score(candidat_ideal(), AUJOURDHUI) == 100


def test_candidat_vide_ne_plante_pas():
    assert calculer_score({}, AUJOURDHUI) == 5  # seuls 0 an d'expérience rapportent 5 points


def test_exemple_du_readme_donne_69():
    candidat = {
        "competences": ["javascript", "html_css", "python", "git"],
        "experience": 1,
        "motivation": ("x" * 300) + " apprendre projet equipe",
        "disponibilite": AUJOURDHUI + timedelta(days=14),
        "lien": "https://github.com/exemple",
    }
    assert calculer_score(candidat, AUJOURDHUI) == 69
    assert categorie(69) == "À étudier"


def test_seuils_de_categorie():
    assert categorie(70) == "À examiner en priorité"
    assert categorie(69) == "À étudier"
    assert categorie(40) == "À étudier"
    assert categorie(39) == "Faible adéquation"


def test_competence_en_double_ou_inconnue():
    detail = calculer_detail({"competences": ["python", "python", "cobol"]}, AUJOURDHUI)
    assert detail["competences"] == 8


def test_mots_cles_plafonnes_a_10_points():
    texte = "apprendre projet equipe contribuer skullvi stage evoluer passion"
    assert score_motivation(texte) == 10  # texte court (0) + 8 mots-clés plafonnés à 10


def test_mots_cles_ignorent_accents_et_majuscules():
    assert score_motivation("ÉQUIPE") == 2


def test_disponibilite():
    assert calculer_detail({"disponibilite": AUJOURDHUI}, AUJOURDHUI)["disponibilite"] == 10
    assert calculer_detail({"disponibilite": "2026-10-20"}, AUJOURDHUI)["disponibilite"] == 5
    assert calculer_detail({"disponibilite": "2027-03-01"}, AUJOURDHUI)["disponibilite"] == 0
    assert calculer_detail({"disponibilite": "pas une date"}, AUJOURDHUI)["disponibilite"] == 0


def test_lien():
    assert score_lien("https://github.com/x") == 5
    assert score_lien("github.com/x") == 0
    assert score_lien("") == 0
    assert score_lien(None) == 0
