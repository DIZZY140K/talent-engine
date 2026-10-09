# Talent Engine

Application web simple pour **recevoir des candidatures, les qualifier automatiquement, les scorer et les classer**, afin d'identifier rapidement les profils à examiner en priorité.

Réalisé dans le cadre de l'étape pratique de candidature au stage développeur chez SKULLVI (Human Capital Program).

## Ce que fait l'application

1. **Formulaire de candidature** (`/postuler`) : nom, email, niveau d'études, années d'expérience, compétences, disponibilité, lien GitHub/portfolio, motivation.
2. **Validation côté serveur** : champs obligatoires, format de l'email, valeurs autorisées, longueur de la motivation, doublons d'email refusés.
3. **Score sur 100** calculé automatiquement, avec le détail par critère.
4. **Classement** (`/classement`) : candidats triés par score, avec recherche par nom ou email, filtre par catégorie, compteurs et fenêtre « Voir le détail ».

## La grille de score (100 points)

| Critère | Points | Règle |
|---|---|---|
| Compétences | 40 | JavaScript 8, Python 8, HTML/CSS 6, PHP 6, SQL 6, Git 6 |
| Expérience | 25 | 0 an = 5, 1 an = 15, 2 ans et plus = 25 |
| Motivation | 20 | Longueur (≥ 300 car. = 10, 150-299 = 5, moins = 0) + 2 points par mot-clé pertinent (max 10) |
| Disponibilité | 10 | Immédiate = 10, sous 30 jours = 5, sinon 0 |
| Lien GitHub / portfolio | 5 | Lien valide (http/https) = 5, sinon 0 |

Mots-clés de motivation : apprendre, projet, équipe, contribuer, skullvi, stage, évoluer, passion (comparés sans accents ni majuscules).

**Catégories**

- **70 et plus** : À examiner en priorité
- **40 à 69** : À étudier
- **Moins de 40** : Faible adéquation

### Choix de conception

- **Critères transparents** : la grille est visible et le détail du score est affiché pour chaque candidat.
- **Le niveau d'études n'est pas noté.** Il sert uniquement à identifier le candidat, pour ne pas favoriser le diplôme au détriment des compétences réelles.
- **Le score aide à trier, il ne décide pas** : un membre de l'équipe examine chaque profil.
- La logique de score est isolée dans `scoring.py` (fonctions simples), ce qui permet de la tester et de la modifier facilement.

## Erreurs anticipées

L'application suppose que les utilisateurs peuvent se tromper, ou envoyer volontairement des données invalides. La validation est faite **côté serveur** (le navigateur n'est jamais cru sur parole), dans `validation.py`.

| Situation | Comportement de l'application |
|---|---|
| Champ obligatoire vide (nom, email, niveau, date, motivation) | Candidature refusée, message d'erreur sous le champ, valeurs déjà saisies conservées |
| Email invalide (« abc », « a@b », « @x.com »…) | Refusé avec un message clair |
| Email déjà utilisé, même avec une autre casse | Refusé : un seul dépôt par candidat ; l'email est enregistré en minuscules |
| Expérience négative, décimale, > 50 ou non numérique | Refusée : un entier entre 0 et 50 est exigé |
| Niveau d'études ou compétence inventés (formulaire modifié à la main) | Refusés : seules les valeurs prévues sont acceptées |
| Date de disponibilité invalide (ex. 31/02/2026) | Refusée avec un message |
| Lien dangereux ou incomplet (`javascript:…`, `github.com/x` sans http) | Refusé : le lien doit commencer par http:// ou https:// |
| Motivation trop courte (< 50 caractères) ou trop longue (> 2000) | Refusée |
| Injection SQL dans la recherche (`' OR '1'='1`) | Neutralisée : toutes les requêtes sont paramétrées |
| Code HTML saisi dans le nom | Affiché comme du texte, jamais exécuté (échappement automatique de Jinja2) |
| Candidat « vide » (aucune information utile) | Le calcul du score ne plante pas : il retourne un score faible |
| Même compétence envoyée deux fois | Comptée une seule fois : le score ne peut pas être gonflé |

## Tests automatiques

La logique importante est testée avec pytest (25 tests) : chaque règle de la grille, la validation du formulaire et la base de données. Seul l'affichage (par exemple l'échappement du HTML) a été vérifié à la main.

| Fichier | Tests | Ce qui est vérifié |
|---|---|---|
| `test_scoring.py` | 9 | Candidat idéal = 100 ; candidat vide sans erreur ; exemple du README = 69 ; seuils des catégories ; compétences en double ou inconnues ; mots-clés plafonnés à 10 points et insensibles aux accents et majuscules ; disponibilité ; lien |
| `test_validation.py` | 10 | Formulaire valide ; formulaire vide ; email, expérience, niveau, compétence, date, lien et motivation invalides ; doublons de compétences |
| `test_db.py` | 6 | Ajout et lecture ; doublon d'email refusé ; tri par score décroissant ; recherche et filtre ; injection SQL neutralisée ; compteurs par catégorie |

Les tests de score et de validation portent sur des fonctions pures (sans base ni serveur). Les tests de la base utilisent SQLite en mémoire : aucun risque pour les vraies données.

## Technologies

- **Frontend** : HTML, CSS, Bootstrap 5, JavaScript
- **Backend** : Python, Flask (templates Jinja2)
- **Base de données** : SQLite (requêtes paramétrées)
- **Tests** : pytest (25 tests : scoring, validation, base de données)

## Installation et lancement

Prérequis : Python 3.10 ou plus.

```bash
pip install -r requirements.txt
python app.py
```

Puis ouvrir http://127.0.0.1:5000 dans le navigateur. La base `talent.db` est créée automatiquement au premier lancement.

## Lancer les tests

```bash
pytest
```

(ou `python lancer_tests.py` si pytest n'est pas installé)

## Structure du projet

```
talent-engine/
├── app.py            Routes Flask (formulaire, classement)
├── scoring.py        Calcul du score et des catégories
├── validation.py     Validation des champs du formulaire
├── db.py             Accès à la base SQLite
├── templates/        Pages HTML (Jinja2)
├── static/           CSS et Bootstrap
└── tests/            Tests automatisés
```

## Limites actuelles

À dire franchement, avec les améliorations possibles :

- **Le classement est public** : il n'y a pas de connexion pour les recruteurs. Avec des vraies candidatures, il faudrait protéger `/classement` (authentification).
- **Le score est une aide heuristique** : les mots-clés de motivation sont une mesure simple et imparfaite, et un bon candidat peut mal scorer.
- **Les routes Flask (`app.py`) ont été vérifiées à la main mais ne sont pas encore couvertes par des tests automatiques** (amélioration prévue).
- Pas d'export des résultats (CSV), pas d'envoi d'email de confirmation.
- Les compétences et leurs points sont fixés dans le code (`scoring.py`).
- SQLite convient pour une démo ; une base plus robuste serait nécessaire à grande échelle.

## Usage de l'IA et contribution personnelle

J'ai utilisé **Claude (Anthropic)** comme assistant pendant ce projet.

**Ce que l'IA m'a aidé à faire :**

- discuter et affiner la grille de score ;
- écrire le code Python du backend (`scoring.py`, `validation.py`, `db.py`, `app.py`) et les tests ;
- adapter mes pages HTML en templates Flask.

**Ma contribution personnelle :**

- J'ai conçu et codé moi-même le frontend en HTML/CSS/Bootstrap (formulaire, classement, navbar, styles).
- J'ai corrigé les erreurs de mise en page Bootstrap, rangé et assemblé le projet, installé et lancé l'application.


## Auteur

Bola Bokinda Axel
