<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Brancher `wyat` dans une application

Quelques exemples courts et copiables pour intégrer un modèle de décision dans vos scripts, un serveur local ou une CI (voir aussi [`docs/integration_dev.md`](../docs/integration_dev.md)).

| Fichier | Usage |
|---|---|
| [`pandas_tri.py`](pandas_tri.py) | Trier un `DataFrame` pandas avec une colonne `choix` et une colonne `marge` (et envoyer sous le seuil à `humain`). |
| [`lot_cron.sh`](lot_cron.sh) & [`requete_exemple.jsonl`](requete_exemple.jsonl) | Traiter un fichier de requêtes JSONL en lot avec la commande `wyat decide` (sans écrire de Python). |
| [`serveur_local.sh`](serveur_local.sh) | Lancer le serveur HTTP local (`127.0.0.1:8790`) pour garder le modèle chargé en mémoire. |
| [`webhook_tickets.py`](webhook_tickets.py) | Petit service HTTP qui reçoit un ticket (`POST /ticket`), appelle `wyat`, applique le seuil de marge et écrit une ligne d'audit JSONL. |
| [`garde_http.py`](garde_http.py) | Garde-fou avant un appel d'outil d'agent IA ou le tri d'un e-mail (règles déterministes en Python + appel HTTP local `wyat` + journal d'audit ; testé par [`tests/test_garde_http.py`](../tests/test_garde_http.py)). |
| [`hook_claude_code.py`](hook_claude_code.py) | Hook `PreToolUse` pour Claude Code qui vérifie chaque commande Bash avant son exécution. |
| [`ci/github-actions.yml`](ci/github-actions.yml) | Exemple de workflow GitHub Actions pour vérifier que vos changements d'options ne dégradent pas le score sur `dev`. |
