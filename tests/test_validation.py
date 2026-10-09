import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validation import valider


def formulaire_valide(**changements):
    form = {
        "nom": "Amina Kabila",
        "email": "Amina@Exemple.com",
        "niveau": "bac+3",
        "experience": "2",
        "competences": ["python", "git"],
        "disponibilite": "2026-11-02",
        "lien": "https://github.com/amina",
        "motivation": "Je veux apprendre et contribuer à des projets concrets au sein de SKULLVI.",
    }
    form.update(changements)
    return form


def test_formulaire_valide():
    donnees, erreurs = valider(formulaire_valide())
    assert erreurs == {}
    assert donnees["email"] == "amina@exemple.com"  # normalisé en minuscules
    assert donnees["experience"] == 2
    assert donnees["disponibilite"] == date(2026, 11, 2)


def test_formulaire_vide_est_rejete():
    _, erreurs = valider({})
    assert set(erreurs) == {"nom", "email", "niveau", "experience", "disponibilite", "motivation"}


def test_email_invalide():
    for mauvais in ["", "abc", "a@b", "a b@c.com", "@x.com"]:
        assert "email" in valider(formulaire_valide(email=mauvais))[1]


def test_experience_invalide():
    for mauvaise in ["-1", "51", "2.5", "abc", ""]:
        assert "experience" in valider(formulaire_valide(experience=mauvaise))[1]


def test_niveau_inconnu():
    assert "niveau" in valider(formulaire_valide(niveau="doctorat"))[1]


def test_competence_inconnue():
    assert "competences" in valider(formulaire_valide(competences=["python", "cobol"]))[1]


def test_competence_seule_en_texte_et_doublons():
    donnees, erreurs = valider(formulaire_valide(competences="python"))
    assert erreurs == {} and donnees["competences"] == ["python"]
    donnees, _ = valider(formulaire_valide(competences=["git", "git"]))
    assert donnees["competences"] == ["git"]


def test_date_invalide():
    assert "disponibilite" in valider(formulaire_valide(disponibilite="31/02/2026"))[1]


def test_lien_optionnel_mais_valide_si_rempli():
    assert valider(formulaire_valide(lien=""))[1] == {}
    assert "lien" in valider(formulaire_valide(lien="github.com/x"))[1]
    assert "lien" in valider(formulaire_valide(lien="javascript:alert(1)"))[1]


def test_motivation_trop_courte_ou_trop_longue():
    assert "motivation" in valider(formulaire_valide(motivation="Trop court"))[1]
    assert "motivation" in valider(formulaire_valide(motivation="x" * 2001))[1]
