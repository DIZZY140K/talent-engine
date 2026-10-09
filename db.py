"""Base SQLite : schéma, ajout et lecture des candidats (requêtes toujours paramétrées)."""
import sqlite3

CHEMIN_PAR_DEFAUT = "talent.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS candidates (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nom           TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE COLLATE NOCASE,
    niveau        TEXT NOT NULL,
    experience    INTEGER NOT NULL,
    competences   TEXT NOT NULL,
    disponibilite TEXT NOT NULL,
    lien          TEXT,
    motivation    TEXT NOT NULL,
    s_competences INTEGER NOT NULL,
    s_experience  INTEGER NOT NULL,
    s_motivation  INTEGER NOT NULL,
    s_disponibilite INTEGER NOT NULL,
    s_lien        INTEGER NOT NULL,
    score         INTEGER NOT NULL,
    categorie     TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


class EmailDejaUtilise(Exception):
    """Un candidat avec cet email existe déjà."""


def get_connection(chemin=CHEMIN_PAR_DEFAUT):
    conn = sqlite3.connect(chemin)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn):
    conn.executescript(SCHEMA)
    conn.commit()


def ajouter_candidat(conn, donnees, detail, categorie):
    """Enregistre un candidat. `detail` vient de scoring.calculer_detail()."""
    try:
        conn.execute(
            """INSERT INTO candidates
               (nom, email, niveau, experience, competences, disponibilite, lien, motivation,
                s_competences, s_experience, s_motivation, s_disponibilite, s_lien, score, categorie)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                donnees["nom"], donnees["email"], donnees["niveau"], donnees["experience"],
                ",".join(donnees["competences"]), donnees["disponibilite"].isoformat(),
                donnees["lien"], donnees["motivation"],
                detail["competences"], detail["experience"], detail["motivation"],
                detail["disponibilite"], detail["lien"], sum(detail.values()), categorie,
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise EmailDejaUtilise(donnees["email"]) from e


def lister_candidats(conn, recherche="", categorie=""):
    """Candidats triés par score décroissant, avec recherche et filtre optionnels."""
    requete = "SELECT * FROM candidates WHERE 1=1"
    params = []
    if recherche:
        requete += " AND (nom LIKE ? OR email LIKE ?)"
        params += [f"%{recherche}%", f"%{recherche}%"]
    if categorie:
        requete += " AND categorie = ?"
        params.append(categorie)
    requete += " ORDER BY score DESC, created_at ASC, id ASC"
    return conn.execute(requete, params).fetchall()


def compter_par_categorie(conn):
    lignes = conn.execute("SELECT categorie, COUNT(*) AS n FROM candidates GROUP BY categorie").fetchall()
    return {ligne["categorie"]: ligne["n"] for ligne in lignes}
