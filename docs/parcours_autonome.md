<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Parcours autonome

Vous pouvez faire l'atelier **seul**, **à deux** ou **guidé par votre assistant de code IA** (en lui disant *« Anime-moi l'atelier »*, voir [`AGENTS.md`](../AGENTS.md)).

## 1. Préparer (une seule fois)

```sh
./scripts/installer.sh           # installe l'environnement et le modèle local (1,82 Go)
source .venv/bin/activate
atelier info && atelier preparer # vérifie la machine et crée le dossier travail/
```

*(Si votre machine est lente ou sans modèle, ajoutez `--secours` : `atelier --secours verifier 1`.)*

## 2. Comment fonctionne chaque étape

Dans chaque dossier de [`missions/`](../missions/README.md), ouvrez `MISSION.md` :
1. **Observez** ce qui se passe sur un exemple concret (souvent une approche naïve comparée à `wyat`).
2. **Comprenez pourquoi** le modèle réagit ainsi.
3. **Modifiez votre fichier dans `travail/`** et lancez `atelier verifier N` (les indices 1 → 2 → 3 vous aident avant de regarder `missions/solutions/`).

## 3. Les 7 étapes

| Étape | Ce que vous faites et pourquoi | Fichier à modifier | Vérifier |
|---|---|---|---|
| **1 · [Première décision](../missions/1_premiere_decision/MISSION.md)** | Comparer un tri par mots-clés (`45/63`) à `wyat` (`55/63`), puis écrire 3 messages pour voir quand la **marge** est haute ou basse. | `travail/mission1.toml` | `atelier verifier 1` |
| **2 · [Cadrer](../missions/2_cadrer/MISSION.md)** | Voir pourquoi une option fourre-tout (« pas sûr ») attire même les messages clairs, et décrire clairement chaque option + son action. | `travail/cadrage.toml` | `atelier verifier 2` |
| **3 · [Accord humain](../missions/3_accord/MISSION.md)** | Étiqueter 15 messages à plusieurs, mesurer l'accord ($\kappa$) et comprendre pourquoi on garde un **test scellé** de côté. | `travail/annotations.csv` | `atelier verifier 3` |
| **4 · [Réparer une option](../missions/4_reparer_option/MISSION.md)** | Une option `facturation` trop courte fait chuter le score de `87,3 %` à `76,2 %` : réparez sa définition en regardant les erreurs sur `dev`. | `travail/options.toml` | `atelier verifier 4` |
| **5 · [Choisir un seuil](../missions/5_politique_de_decision/MISSION.md)** | Les erreurs ont une marge basse (`0,12` en médiane contre `0,92`) : choisissez un **seuil de marge** (`atelier seuils`) pour envoyer les cas douteux à un humain. | `travail/politique.toml` | `atelier verifier 5` |
| **6 · [Garde-fou sécurité](../missions/6_garde_fou_securite/MISSION.md)** | Bloquer les commandes shell dangereuses d'un agent IA et les SMS d'arnaque en combinant règles de code, `wyat` et seuil bas. | `travail/securite.toml` *(ou `garde.py`)* | `atelier verifier 6` |
| **7 · [Votre propre cas](../missions/7_votre_cas/MISSION.md)** | Prendre un petit script dans [`cas_usage/`](../cas_usage/README.md) et l'adapter à votre besoin : les **mots** au modèle, les **chiffres et règles** au code. | `travail/mon_cas/` | — |

## 4. Ouvrir le test scellé (une seule fois, à la fin)

Une fois vos options (`étape 4`), votre seuil (`étape 5`) et votre garde-fou (`étape 6`) figés, ouvrez le **test scellé** sur des messages jamais vus :

```sh
ATELIER_ANIMATEUR=1 atelier verifier 4 --final
ATELIER_ANIMATEUR=1 atelier verifier 5 --final
ATELIER_ANIMATEUR=1 atelier verifier 6 --final
```

Vous verrez le score baisser par rapport à `dev` (`87,3 %` → `74,0 %`) : c'est normal et c'est la leçon la plus utile de l'atelier — un jeu de données qu'on regarde pour régler ses options finit toujours par flatter le modèle.
