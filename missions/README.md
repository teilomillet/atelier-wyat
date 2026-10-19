<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Les 7 étapes de l'atelier

Chaque étape part d'un cas concret, montre ce qui se passe (souvent une approche simple ou naïve comparée à `wyat`), explique **pourquoi**, puis vous propose un petit fichier à modifier dans `travail/`.

```sh
atelier preparer        # crée les fichiers de départ dans travail/ (sans rien écraser)
atelier verifier 1      # vérifie l'étape 1 sur le jeu dev
```

| # | Étape | Ce qu'on comprend | Fichier | Vérification |
|---|---|---|---|---|
| 1 | [Première décision](1_premiere_decision/MISSION.md) | Un modèle de décision choisit parmi des options fermées et donne une **marge** quand il doute (`45/63` par mots-clés → `55/63` avec `wyat`). | `travail/mission1.toml` | `atelier verifier 1` |
| 2 | [Cadrer la décision](2_cadrer/MISSION.md) | Une option fourre-tout (« pas sûr ») aspire les messages clairs ; le doute se gère par la marge, pas par une case floue. | `travail/cadrage.toml` | `atelier verifier 2` |
| 3 | [Accord humain](3_accord/MISSION.md) | Deux humains ne sont pas toujours d'accord ($\kappa$) : on sépare un jeu `dev` (pour régler) et un **test scellé** (pour vérifier une seule fois). | `travail/annotations.csv` | `atelier verifier 3` |
| 4 | [Réparer une option](4_reparer_option/MISSION.md) | Le libellé d'une option est sa définition : oublier 4 mots dans `facturation` fait perdre 11 points (`87,3 %` → `76,2 %`). | `travail/options.toml` | `atelier verifier 4` |
| 5 | [Choisir un seuil](5_politique_de_decision/MISSION.md) | Plutôt que « tout automatiser » ou « tout relire », un **seuil de marge** envoie les cas douteux à un humain (`atelier seuils`). | `travail/politique.toml` | `atelier verifier 5` |
| 6 | [Garde-fou sécurité](6_garde_fou_securite/MISSION.md) | Filtrer les commandes shell d'un agent IA et les SMS d'arnaque en combinant règles de code, `wyat` et validation humaine. | `travail/securite.toml` *(ou `garde.py`)* | `atelier verifier 6` |
| 7 | [Votre propre cas](7_votre_cas/MISSION.md) | Adapter un script de [`cas_usage/`](../cas_usage/README.md) à votre projet : les **mots** au modèle, les **chiffres et règles** au code. | `travail/mon_cas/` | — |

> **Le test scellé** ne s'ouvre qu'une seule fois, à la fin, quand vos réglages sont terminés : `ATELIER_ANIMATEUR=1 atelier verifier N --final`.
