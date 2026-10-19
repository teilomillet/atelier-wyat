<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# De l'atelier à votre entreprise

*Une décision fermée, des exemples étiquetés, un test scellé, un seuil choisi selon le coût. Le modèle n'est qu'une pièce.*

## La recette en 5 étapes

| # | Étape | Ce qu'on produit | Repère |
|---|---|---|---|
| 1 | **Choisir une décision avec une action claire** | « Quand X arrive, on fait A, B ou C » | Si vous ne savez pas quoi *faire* de chaque réponse, ce n'est pas encore une décision |
| 2 | **Écrire les options** | question + 2 à 8 options + l'action de chaque option | Décrire ce que l'option *couvre*, avec les mots des clients ; pas d'option « autre / pas sûr » fourre-tout (l'incertitude se gère par la marge) |
| 3 | **Réunir 50 à 200 vrais exemples, les étiqueter à plusieurs** | `dev.csv` + `test_scelle.csv` | Mesurer l'accord (kappa) sur 20 à 30 exemples avant d'étiqueter le reste ; écrire les règles d'étiquetage |
| 4 | **Évaluer sur le test scellé, avec un intervalle de confiance** | exactitude [IC 95 %], erreurs, calibration | On règle tout sur dev ; le test s'ouvre une fois, options figées. 77 exemples ≈ ±10 points ; ±3 points ≈ 800 |
| 5 | **Choisir le seuil selon le coût, mettre en service avec repli humain, surveiller** | seuil de marge, journal, tableau de bord | Coût d'une erreur vs coût d'une relecture ; journaliser entrée (ou son empreinte), options, choix, marge, `model_id` ; rouvrir un test frais chaque mois |

## Brancher wyat chez vous (code minimal, tout en local)

**Dans un script ou un notebook (pandas)** — `integrations/pandas_tri.py`
```python
d = modele.decide(wyat.Request.choice(QUESTION, OPTIONS, context=texte))
df["suite"] = [modele.decide(wyat.Request.choice(QUESTION, OPTIONS, context=t)).selected for t in df.texte]
```

**En service HTTP local** (FastAPI fourni par `wyat[server]`) — un seul processus garde le modèle en mémoire
```sh
.venv/bin/wyat serve teilomillet/wyat-1-800m --backend mlx        # ou --backend torch ; écoute sur 127.0.0.1:8000
curl -s localhost:8000/v1/decide -H 'Content-Type: application/json' \
  -d '{"task":"choice","query":"Quel service ?","candidates":[{"id":"paiement","text":"Paiement, double débit"},{"id":"livraison","text":"Colis, livraison"}],"context":"Débité deux fois"}'
```

**En lot de nuit (cron)** — `integrations/lot_cron.sh` : une requête JSON par ligne → `wyat decide` → une décision par ligne.
```sh
30 2 * * *  /chemin/wyat-atelier/integrations/lot_cron.sh demandes.jsonl decisions.jsonl
```

**Sur l'outil de tickets ou la boîte mail** — `integrations/webhook_tickets.py` : `POST /ticket` → `{"file": "paiement", "marge": 0.87}` ; sous le seuil → `humain`. Chaque décision est journalisée.

**Avant chaque commande d'un agent de code** (hook `PreToolUse` de Claude Code) — `integrations/hook_claude_code.py` : règles écrites → liste blanche → wyat (via `wyat serve`) → `allow` / `ask` / `deny`. Serveur injoignable → `ask`, jamais `allow`.
```json
{"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command",
  "command": "python3 /chemin/wyat-atelier/integrations/hook_claude_code.py", "onFailure": "block"}]}]}}
```

**En CI** : `atelier verifier N` ou un petit `pytest` sur vos exemples (comme `tests/`) : une modification des options qui fait baisser le score sur dev casse la construction.

## Liste de contrôle avant la mise en service

- [ ] **RGPD** : base légale pour réutiliser les messages comme exemples ; anonymiser le jeu d'évaluation ; tout reste en local (pas de sous-traitant) ; durée de conservation du journal.
- [ ] **Décision automatisée** : si elle produit un effet important sur une personne (recrutement, crédit, sanction…), pas de décision 100 % automatique ; un humain décide, wyat aide seulement (et vérifier l'absence de biais).
- [ ] **Journal** : entrée ou son empreinte, options (version), choix, probabilités, marge, `model_id`, date. Sans journal, pas d'audit.
- [ ] **Repli humain** : sous le seuil de marge, ou pour les options sensibles (décès, menace juridique), toujours une personne.
- [ ] **Dérive** : chaque mois, 50 messages récents étiquetés ; comparer avec le test scellé ; alerte si l'exactitude ou la part automatisée bouge de plus de 5 points.
- [ ] **Règles écrites à côté du modèle** : formats (IBAN, carte, téléphone), montants, listes blanches de domaines : c'est le travail du code.
- [ ] **Licence** : poids de wyat-1-800M **non commerciaux** ; pour un usage commercial, autre modèle ou accord.

## Quand NE PAS utiliser un modèle de décision

- Il faut **écrire** (réponse, résumé, extraction d'un champ) → un modèle génératif.
- Les options ne sont pas fermées, ou changent à chaque fois.
- La règle est **exacte et connue** (comparer un montant à un plafond, vérifier un format, une date) → du code : plus simple, plus sûr, explicable.
- Il faut raisonner en plusieurs étapes, ou enchaîner des actions (piloter un agent : voir le cas 11, résultats faibles).
- Une erreur rare est inacceptable et rien ne la rattrape derrière.

*Galerie : `cas_usage/` (26 cas par secteur, résultats réels, ce qui marche et ce qui ne marche pas ; licence des poids : `docs/licence_du_modele.md`). Données de l'atelier synthétiques, entreprise et personnes fictives.*
