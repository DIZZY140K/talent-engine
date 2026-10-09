"""Talent Engine : application Flask (formulaire de candidature + classement)."""
import os
from datetime import date

from flask import Flask, redirect, render_template, request, url_for

import db
from scoring import calculer_detail, categorie
from validation import valider

app = Flask(__name__)
CHEMIN_BASE = os.environ.get("TALENT_DB", db.CHEMIN_PAR_DEFAUT)

COULEURS = {
    "À examiner en priorité": "warning",
    "À étudier": "primary",
    "Faible adéquation": "secondary",
}


@app.template_global()
def couleur(nom_categorie):
    """Couleur Bootstrap associée à une catégorie (badge et barre de progression)."""
    return COULEURS.get(nom_categorie, "secondary")


def connexion():
    conn = db.get_connection(CHEMIN_BASE)
    db.init_db(conn)
    return conn


@app.get("/")
def accueil():
    return redirect(url_for("postuler"))


@app.route("/postuler", methods=["GET", "POST"])
def postuler():
    if request.method == "GET":
        return render_template(
            "index.html", valeurs={"competences": []}, erreurs={}, envoye=request.args.get("envoye") == "1"
        )

    form = request.form.to_dict()
    form["competences"] = request.form.getlist("competences")
    donnees, erreurs = valider(form)

    if not erreurs:
        detail = calculer_detail(donnees, date.today())
        conn = connexion()
        try:
            db.ajouter_candidat(conn, donnees, detail, categorie(sum(detail.values())))
        except db.EmailDejaUtilise:
            erreurs["email"] = "Une candidature existe déjà avec cet email."
        finally:
            conn.close()
        if not erreurs:
            return redirect(url_for("postuler", envoye=1))

    return render_template("index.html", valeurs=form, erreurs=erreurs, envoye=False), 400


@app.get("/classement")
def classement():
    conn = connexion()
    try:
        candidats = db.lister_candidats(conn)
    finally:
        conn.close()
    return render_template("classement.html", candidats=candidats)


if __name__ == "__main__":
    app.run(debug=True)
