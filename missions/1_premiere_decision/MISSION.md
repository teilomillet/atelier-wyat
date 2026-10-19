<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Étape 1 — Une première décision

**Situation.** Lundi matin : une boîte de support client reçoit des centaines de messages qu'il faut envoyer vers le bon service (`facturation`, `technique`, `resiliation`, `livraison`, `autre`), 100 % en local.

**Ce qui se passe et pourquoi**
1. **Ce qu'on observe (`exemples/00_natif_contre_wyat.py`).** Une règle rapide par mots-clés (`factur`, `colis`, `internet`…) fait **45/63** sur `dev` : dès qu'un client formule autrement (*« ma carte SIM n'est pas activée »*) ou parle de deux sujets à la fois, elle se trompe — et surtout **elle ne dit jamais « je ne sais pas »**.
2. **La question.** Quand un humain trie un message en une demi-seconde, rédige-t-il un texte ou choisit-il parmi 5 cases connues ? Et que fait-il quand un message mélange deux demandes ?
3. **Pourquoi `wyat` change la donne.** Au lieu de générer du texte libre, `wyat` reçoit une liste fermée d'options, calcule une **probabilité par option** (**55/63** sur `dev`) et mesure l'écart entre la 1re et la 2e option : la **marge** (`probability_margin`). Proche de `1,0`, le modèle est sûr ; proche de `0,0`, il hésite.

**À vous de jouer** : modifiez `travail/mission1.toml`
Écrivez vos propres messages pour voir quand la marge est haute et quand elle chute :
```toml
[[messages]]
texte = "on m'a prélevé deux fois ce mois-ci"
attendu = "facturation"     # facturation, technique, resiliation, livraison ou autre
```

**Vérifier** (`atelier verifier 1`)
- au moins **3 messages** écrits par vous ;
- au moins **2 messages** classés dans `attendu` avec une **marge ≥ 0,8** ;
- au moins **1 message** qui fait hésiter le modèle (**marge < 0,3**).

**Pour tester directement** : `atelier decider "votre message"`, `python exemples/00_natif_contre_wyat.py` ou `python exemples/01_une_decision_wyat.py`.

**Indices**
1. Pour une marge haute : écrivez une demande simple à un seul sujet (*prélèvement*, *colis*, *box en panne*).
2. Pour une marge basse (`< 0,3`) : mettez deux sujets dans la même phrase, ou un message flou sans aucun indice.
3. Essayez par exemple *« SVP rappelez-moi, c'est urgent »* (`marge ≈ 0,09`).
