<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Parcours développeur : intégrer wyat dans du code, avec la sécurité comme fil conducteur

Tout tourne en local. Le serveur HTTP écoute sur **127.0.0.1:8790** (jamais sur une interface publique).

## 1. API Python (étape 1)
```python
import wyat
modele = wyat.load("/chemin/vers/wyat-1-800m/model", backend="mlx")      # "torch" sur Linux / PC ; un chemin = aucun téléchargement
d = modele.decide(wyat.Request.choice("Quel service doit traiter ce message ?",
                                      {"facturation": "Facturation : débits, prélèvements, remboursements",
                                       "technique": "Technique : box, internet, mobile en panne"},
                                      context="On m'a prélevé deux fois ce mois-ci"))
d.selected, d.probabilities_by_id, d.probability_margin, d.model_id      # choix, probabilité par option, marge, empreinte
p = modele.decide(wyat.Request.noul("Cet e-mail est-il une tentative d'hameçonnage ?", context=texte)).probability_true
s = modele.decide(wyat.Request.score("Priorité ?", ["P4 …", "P3 …", "P2 …", "P1 …"], context=alerte)).expected_ordinal_value
```
Exemples complets : `exemples/01_une_decision_wyat.py`, `cas_usage/*/cas.py`.

## 2. Ligne de commande, en lot (JSONL)
```sh
.venv/bin/wyat decide "$WYAT_MODEL" --backend torch < integrations/requete_exemple.jsonl > decisions.jsonl
```
Une requête par ligne (`task`, `query`, `candidates`, `context`), une décision par ligne. Planification : `integrations/lot_cron.sh`.

## 3. Serveur HTTP local
```sh
./integrations/serveur_local.sh            # wyat serve … --host 127.0.0.1 --port 8790
curl -s 127.0.0.1:8790/v1/decide -H 'Content-Type: application/json' \
  -d '{"task": "noul", "query": "Cet e-mail est-il une tentative d hameçonnage ?", "context": "Votre mot de passe expire, cliquez ici"}'
```
Réponse : `model_id`, `selected`, `ranking`, `probabilities` (ordre des options ; pour un oui / non : `false`, `true`). Le champ `context` doit être un **texte** (sérialisez un objet en JSON). Mesuré sur Mac M4 Pro : ≈ 0,16 s par requête.

## 4. Garde-fous avant exécution (étape 6, cas 12, 14, 15, 16)
`integrations/garde_http.py` : avant chaque appel d'outil d'un agent, une question de concordance au serveur local, puis une **politique en code** :
- outil inconnu → refuser ; instruction suspecte dans les arguments → refuser ;
- concordance < 0,6 → refuser ;
- destinataire hors domaines internes, outil externe ou irréversible → **confirmation humaine** ;
- sinon exécuter.

Ce que l'exemple montre (sortie réelle) : pour « envoie le compte rendu à Paul Martin », un appel vers une adresse personnelle obtient P(concordance) = 0,87, presque autant que le bon appel (0,86). **C'est la règle de code sur le domaine qui l'arrête**, pas le modèle. Même leçon que le cas 14.

Commandes shell d'un agent de code : `integrations/hook_claude_code.py` (hook `PreToolUse`) et `atelier/securite.py` (liste blanche → règles → wyat → vérifications).

## 5. Hameçonnage et triage des e-mails (cas 13)
Trois issues : classer (< 0,25), **analyste** (zone grise, abstention), quarantaine (≥ 0,75 ou règle). `politique_email` dans `integrations/garde_http.py`.

## 6. Injection et entrées suspectes (cas 16)
Seuil bas, règles pour les motifs connus, et surtout : un assistant qui lit des contenus externes **n'a pas d'outils dangereux**. Les injections subtiles passent (P = 0,04 à 0,30 dans le cas 16).

## 7. Abstention, seuils, calibration (étape 5)
Le seuil se choisit **sur dev**, selon le coût d'une erreur, puis se vérifie **une fois** sur le test scellé. `exemples/04_balayer_les_seuils.py`, `atelier seuils`. En sécurité, choisissez le seuil qui ne laisse passer aucun cas dangereux sur dev, et acceptez les validations en plus.

## 8. Journal et audit (cas 14, 21, `garde_http.py`)
Une ligne JSON par décision : horodatage, empreinte du modèle (`model_id`), version de la politique, entrée, probabilités, action, raison. Le journal est local ; versez-le dans votre SIEM.

## 9. Tests en CI
- `tests/test_garde_http.py` : ce que la politique doit garantir **quelle que soit la probabilité** (outil inconnu refusé, virement toujours confirmé, destinataire externe jamais exécuté seul). Sans modèle, en 0,01 s.
- `tests/test_atelier.py` : missions et mesures, sur les décisions pré-calculées.
- `integrations/ci/github-actions.yml` : exemple de CI, tests sans modèle à chaque push, cas réels sur demande (une sortie qui change = à relire).
