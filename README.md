<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Apprendre les modèles de décision avec `wyat`

Ce dépôt est un guide pratique (et un atelier 100 % local) pour comprendre ce qu'est un **modèle de décision**, comment s'en servir en quelques lignes de Python, et où sont ses limites.

Pas besoin d'être expert en IA ni d'avoir un gros serveur : rien qu'en lisant cette page, vous aurez compris l'essentiel — et si vous voulez tester, tout tourne sur un simple ordinateur portable.

---

## 1. C'est quoi un modèle de décision ? (en 30 secondes)

Imaginez que vous deviez trier automatiquement des messages entrants vers le bon service (`facturation`, `technique`, `resiliation`, `livraison`, `autre`) :

- **Avec des mots-clés (`if "facture" in message`)** : c'est rapide à coder, mais dès qu'un client formule autrement (*« on m'a débité deux fois »*, *« ma carte SIM n'est pas activée »*), ça tombe à côté (`45/63` sur notre jeu d'essai). Surtout, un `if` **ne sait jamais dire « je ne suis pas sûr »**.
- **Avec un LLM génératif (chatbot)** : il rédige du texte mot à mot. C'est lourd, lent, et il faut parser sa réponse en espérant qu'il n'invente pas une catégorie.
- **Avec un modèle de décision (`wyat`)** : il ne rédige **jamais** de texte. Vous lui donnez une question et **votre liste fermée d'options** ; il calcule directement la **probabilité de chaque option** et l'écart entre la 1re et la 2e option : la **marge de confiance** (`probability_margin`).

---

## 2. Ce que ça donne en 10 lignes de Python

```python
import wyat

modele = wyat.load()  # charge wyat-1-800m en local (≈ 0,15 s par décision sur Mac)

options = {
    "facturation": "Facturation : factures, débits, prélèvements, remboursements",
    "technique":   "Technique : panne internet, wifi, box, mobile, carte SIM",
    "resiliation": "Résiliation : mettre fin à un abonnement ou fermer une ligne",
}

for message in [
    "On m'a prélevé deux fois 29,99 € ce mois-ci",
    "La box clignote rouge depuis hier soir",
    "J'ai résilié en août et vous continuez de me prélever !",
]:
    d = modele.decide(wyat.Request.choice("Quel service doit traiter ce message ?", options, context=message))
    action = d.selected if d.probability_margin >= 0.5 else "-> passer à un humain"
    print(f"{message:<58} => {action} (marge {d.probability_margin:.2f})")
```

**Sortie réelle :**
```text
On m'a prélevé deux fois 29,99 € ce mois-ci                => facturation           (marge 0.99)
La box clignote rouge depuis hier soir                     => technique             (marge 0.48)
J'ai résilié en août et vous continuez de me prélever !    => -> passer à un humain (marge 0.25)
```

Sur le 3e message, le client parle **à la fois** de résiliation et de prélèvement : la marge chute (`0.25`), votre `if d.probability_margin >= 0.5` le voit tout de suite et passe le message à un humain au lieu de faire une erreur en silence.

---

## 3. Les 3 seules questions qu'on peut poser à `wyat`

L'API tient en trois types de requêtes ([`docs/integration_dev.md`](docs/integration_dev.md)) :

1. **Choisir parmi une liste — `Request.choice(question, options, context=...)`**
   Renvoie l'option gagnante (`d.selected`), la probabilité de chaque option (`d.probabilities_by_id`) et la marge (`d.probability_margin`).
2. **Répondre oui ou non — `Request.noul(question, context=...)`** *(« noul » = oui/non)*
   Renvoie directement la probabilité du « oui » (`d.probability_true`, entre `0.0` et `1.0`). Pratique pour : *« Cet e-mail ressemble-t-il à du phishing ? »* ou *« Cette commande shell envoie-t-elle des données hors de la machine ? »*.
3. **Noter sur une échelle ordonnée — `Request.score(question, niveaux, context=...)`**
   Renvoie une note moyenne pondérée (`d.expected_ordinal_value`, par exemple de `0` à `3` pour `P4` → `P1`).

---

## 4. Les 4 leçons essentielles de l'atelier

Même sans lancer le code, voici les quatre pièges classiques que l'atelier fait découvrir par l'expérience :

1. **Le texte de l'option est sa définition ([Étape 4](missions/4_reparer_option/MISSION.md))**
   Le modèle ne connaît pas votre entreprise. Si vous écrivez juste `"Facturation"`, il plafonne à `65 %` (`41/63`). Si vous décrivez ce que contient l'option avec les mots des clients (*« montant d'une facture, débits ou prélèvements bancaires, remboursement »*), il passe à **`87 %` (`55/63`)** — sans ré-entraîner le modèle.
2. **Ne mettez jamais d'option fourre-tout « pas sûr / divers » ([Étape 2](missions/2_cadrer/MISSION.md))**
   Si vous ajoutez une option *« Pas sûr : demander à un humain »*, elle attire même des pannes évidentes (*« ma box clignote rouge »* part dans `pas_sur` à `48 %`). Gérez toujours le doute **après coup avec un seuil sur la marge**, jamais avec une option floue.
3. **Les mots au modèle, les chiffres et les règles exactes au code ([Étape 6](missions/6_garde_fou_securite/MISSION.md) & [Cas d'usage](cas_usage/README.md))**
   `wyat` est un petit modèle (`0,8` milliard de paramètres) très bon pour comprendre l'intention d'une phrase, mais mauvais pour comparer des prix ou vérifier un format. Vérifiez les montants (`> 50 €`), dates, IBAN, listes blanches et commandes interdites (`rm -rf /`) avec de simples `if` en Python, et utilisez `wyat` sur le texte.
4. **Gardez toujours un jeu de test « scellé » de côté ([Étapes 3 et 5](missions/5_politique_de_decision/MISSION.md))**
   Quand on ajuste ses options en regardant les erreurs sur un jeu d'essai (`dev`, `87,3 %`), on finit toujours par coller aux exemples qu'on a sous les yeux. Sur 77 nouveaux messages jamais vus (**test scellé**), le score réel est de **`74,0 %` (`57/77`)**.

---

## 5. Tester sur votre machine (en 2 minutes)

Prérequis : Python 3.12+ et [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`).

```sh
./scripts/installer.sh                              # installe .venv + télécharge le modèle (1,82 Go)
.venv/bin/python exemples/00_natif_contre_wyat.py   # compare mots-clés (45/63) et wyat (55/63)
.venv/bin/python exemples/01_une_decision_wyat.py   # votre première décision en 15 lignes
```

> **Pas envie de télécharger les 1,82 Go du modèle ?**
> Toutes les commandes de l'atelier ont un mode **`--secours`** (ou `WYAT_PRECALCULE=1`) qui rejoue instantanément les vraies décisions pré-calculées :
> ```sh
> WYAT_PRECALCULE=1 .venv/bin/python exemples/00_natif_contre_wyat.py
> ```

---

## 6. Comment explorer le dépôt ?

Choisissez ce qui vous convient le mieux :

- **Par de petits scripts prêts à lancer**
  - [`exemples/`](exemples/README.md) : **7 scripts très courts** (de 15 à 45 lignes) pour découvrir chaque brique une par une.
  - [`cas_usage/`](cas_usage/README.md) : **26 cas concrets** (~30 lignes chacun : tri de tickets, garde-fou de commandes d'agent IA, détection de phishing, notes de frais, mairie, industrie, e-commerce), avec la vraie sortie enregistrée.
  - [`integrations/`](integrations/README.md) : comment brancher `wyat` dans un script `pandas`, un cron, un petit serveur HTTP local, un hook Claude Code ou une CI GitHub Actions.
- **Par le parcours guidé en 7 étapes** ([`missions/`](missions/README.md) et [`docs/parcours_autonome.md`](docs/parcours_autonome.md))
  ```sh
  source .venv/bin/activate
  atelier preparer        # crée vos fichiers d'exercice dans travail/
  atelier verifier 1      # corrige l'étape 1 et donne des indices progressifs
  ```
- **Avec votre assistant de code IA** *(Claude Code, Cursor, Codex, Gemini CLI, Copilot, Antigravity)*
  Ouvrez ce dépôt et demandez-lui simplement : **« Anime-moi l'atelier »** ou **« Explique-moi l'étape 1 »** ([`AGENTS.md`](AGENTS.md)).
- **Dans Jupyter ou en atelier d'équipe**
  - [`notebooks/`](notebooks/README.md) : 5 notebooks interactifs (et leurs versions déjà exécutées dans `notebooks/executes/`).
  - [`docs/guide_animateur.md`](docs/guide_animateur.md) et [`docs/fiches/`](docs/fiches/) : pour animer une session de 2 h à plusieurs.

---

## Aller plus loin & Licence

- **Documentation rapide** : [`docs/integration_dev.md`](docs/integration_dev.md) (API Python, CLI, HTTP) · [`docs/benchmarks.md`](docs/benchmarks.md) (comparaisons honnêtes et limites) · [`docs/deploiement_hors_ligne.md`](docs/deploiement_hors_ligne.md) (utiliser sans réseau) · [`docs/conformite.md`](docs/conformite.md) (RGPD, AI Act, journal d'audit).
- **Modèles sur mesure & usage en production** : les poids `wyat-1-800m` sont gratuits pour apprendre, tester et évaluer ([`docs/licence_du_modele.md`](docs/licence_du_modele.md)). Pour une licence commerciale ou pour construire un **modèle de décision sur mesure** adapté à vos données, contactez [Teïlo Millet](https://github.com/teilomillet).
- **Licence du dépôt** : **PolyForm Noncommercial 1.0.0** ([`LICENSE`](LICENSE) et [`NOTICE`](NOTICE)) — libre de lire, exécuter, modifier et partager à titre non commercial en citant **Teïlo Millet** (revente commerciale interdite sans accord écrit). La bibliothèque `wyat` est sous Apache-2.0.
