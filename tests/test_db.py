import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db import EmailDejaUtilise, ajouter_candidat, compter_par_categorie, get_connection, init_db, lister_candidats
from scoring import calculer_detail, categorie


def nouvelle_base():
    conn = get_connection(":memory:")
    init_db(conn)
    return conn


def candidat(nom="Amina", email="amina@exemple.com", competences=("python", "git"), experience=1):
    return {
        "nom": nom, "email": email, "niveau": "bac+3", "experience": experience,
        "competences": list(competences), "disponibilite": date(2026, 10, 7),
        "lien": "https://github.com/x", "motivation": "Je veux apprendre en équipe.",
    }


def enregistrer(conn, donnees):
    detail = calculer_detail(donnees, date(2026, 10, 7))
    ajouter_candidat(conn, donnees, detail, categorie(sum(detail.values())))


def test_ajout_et_lecture():
    conn = nouvelle_base()
    enregistrer(conn, candidat())
    lignes = lister_candidats(conn)
    assert len(lignes) == 1
    assert lignes[0]["competences"] == "python,git"
    assert lignes[0]["score"] == (
        lignes[0]["s_competences"] + lignes[0]["s_experience"] + lignes[0]["s_motivation"]
        + lignes[0]["s_disponibilite"] + lignes[0]["s_lien"]
    )


def test_doublon_d_email_refuse_meme_avec_une_autre_casse():
    conn = nouvelle_base()
    enregistrer(conn, candidat())
    try:
        enregistrer(conn, candidat(nom="Autre", email="AMINA@exemple.com"))
        assert False, "le doublon aurait dû être refusé"
    except EmailDejaUtilise:
        pass
    assert len(lister_candidats(conn)) == 1


def test_classement_par_score_decroissant():
    conn = nouvelle_base()
    enregistrer(conn, candidat("Faible", "a@x.com", competences=(), experience=0))
    enregistrer(conn, candidat("Fort", "b@x.com", competences=("python", "javascript", "git"), experience=3))
    assert [c["nom"] for c in lister_candidats(conn)] == ["Fort", "Faible"]


def test_recherche_et_filtre():
    conn = nouvelle_base()
    enregistrer(conn, candidat("Amina", "amina@x.com"))
    enregistrer(conn, candidat("Karim", "karim@x.com"))
    assert [c["nom"] for c in lister_candidats(conn, recherche="kar")] == ["Karim"]
    assert lister_candidats(conn, categorie="Catégorie inexistante") == []


def test_injection_sql_neutralisee():
    conn = nouvelle_base()
    enregistrer(conn, candidat())
    assert lister_candidats(conn, recherche="' OR '1'='1") == []
    assert len(lister_candidats(conn)) == 1


def test_compteurs():
    conn = nouvelle_base()
    enregistrer(conn, candidat("A", "a@x.com"))
    enregistrer(conn, candidat("B", "b@x.com"))
    assert sum(compter_par_categorie(conn).values()) == 2
