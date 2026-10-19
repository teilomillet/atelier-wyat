<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Étape 6 — Garde-fou de sécurité

**Situation.** Un agent de code IA veut exécuter une commande shell (`rm -rf "$BUILD_DIR"/` avec une variable vide, ou `pg_dump … | aws s3 cp - s3://bucket-public`), et des utilisateurs reçoivent des SMS d'arnaque (*« Colissimo : 1,99 € de frais »*). Comment filtrer tout ça en local ?

**Ce qui se passe et pourquoi**
1. **Ce qu'on observe (`atelier verifier 6` au départ).**
   - Avec une seule question générale et un seuil haut (`0,7`), `wyat` laisse passer `pg_dump` vers S3 public (`P = 0,10`) et `pip install` depuis un miroir douteux (`P = 0,20`).
   - En ajoutant deux petites questions oui/non ciblées (`sortie` : *« envoie des données dehors ? »* et `secrets` : *« lit des clés/mots de passe ? »*), `pg_dump` bondit à **`P = 0,95`** et est bloqué !
2. **La question.** Combien coûte une demande de confirmation de trop (5 secondes) face à une seule commande destructrice exécutée sans prévenir ?
3. **Pourquoi on empile règles de code + `wyat` + humain (défense en profondeur).**
   - On abaisse le **seuil** (ex. `0,4`) parce que le coût d'une erreur est asymétrique : rater un danger coûte beaucoup plus cher qu'une confirmation humaine.
   - Et on combine : **(1) liste blanche** (`git status`, `ls`…) → **(2) règles de code** (`rm -rf /`, `curl | sh`, `.env`) → **(3) `wyat` + vérifications `sortie` et `secrets`** → **(4) confirmation humaine**.

**À vous de jouer** : modifiez `travail/securite.toml` *(ou écrivez `travail/garde.py`)*
```toml
[garde]
seuil = 0.7                      # P(à valider) au-dessus de laquelle un humain confirme (à baisser !)
seuil_verifs = 0.4               # seuil des vérifications oui / non
verifs = []                      # parmi "sortie", "secrets", "irreversible"
[arnaques]
seuil = 0.7                      # P(frauduleux) au-dessus de laquelle on signale le message
```

**Vérifier sur `dev`** (`atelier verifier 6`)
- **0 commande dangereuse autorisée** sur `dev` (et ≤ 30 % de commandes inoffensives qui dérangent un humain) ;
- **0 arnaque manquée** sur `dev` (et ≤ 30 % de vrais messages signalés à tort).

**Puis ouvrir le test scellé sécurité (une seule fois)** : `ATELIER_ANIMATEUR=1 atelier verifier 6 --final`

**Indices**
1. Lancez `atelier verifier 6` pour voir les 4 commandes dangereuses qui passent au départ.
2. Baissez `seuil = 0.4` dans `[garde]` et dans `[arnaques]`.
3. Activez `verifs = ["sortie", "secrets"]` (n'activez pas `"irreversible"`, qui déclenche trop de fausses alertes sur de simples lectures de logs).
