<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Étape 5 — Choisir un seuil et ouvrir le test scellé

**Situation.** Avec `87,3 %` (`55/63`) sur `dev`, il reste quand même 8 messages mal routés sur 63. Faut-il tout automatiser (et accepter ces erreurs) ou tout faire relire à la main ?

**Ce qui se passe et pourquoi**
1. **Ce qu'on observe (`atelier seuils`).** Sur `dev`, les bonnes réponses ont une marge médiane de **`0,92`**, alors que les erreurs ont une marge médiane de **`0,12`** : le modèle se trompe surtout quand sa marge est basse !
2. **La question.** Que se passe-t-il si on décide : **au-dessus d'un seuil de marge, le modèle route seul ; en dessous, un humain lit le message** ?
3. **Pourquoi le seuil est un choix simple.** Avec `atelier seuils`, vous voyez l'arbitrage :
   - sans seuil (`0,0`) : **100 %** automatisé, **8 erreurs** sur 63 (`12,7` pour 100) ;
   - à **seuil `0,5`** : **70 %** automatisé (`44/63`), seulement **2 erreurs** (`3,2` pour 100), et `19` messages ambigus envoyés à un humain.

**À vous de jouer** : modifiez `travail/politique.toml` *(sur `dev`)*
```toml
seuil = 0.5                  # marge minimale pour automatiser (en dessous -> humain)
erreurs_max_pour_100 = 5     # votre budget d'erreurs automatiques pour 100 messages
```

**Vérifier sur `dev`** (`atelier verifier 5`)
- erreurs automatiques pour 100 messages **≤ `erreurs_max_pour_100`** ;
- au moins **50 %** des messages automatisés.

**Puis ouvrir le test scellé (une seule fois !)**
Une fois `options.toml` et `politique.toml` figés, ouvrez le test scellé :
```sh
ATELIER_ANIMATEUR=1 atelier verifier 4 --final
ATELIER_ANIMATEUR=1 atelier verifier 5 --final
```
> **Ce que vous verrez** : sur le test scellé, le score descend (`87,3 %` sur `dev` → **`74,0 %` (`57/77`)** sur le test, et `10,4` erreurs pour 100 au seuil `0,5`). Ce n'est pas un bug : régler ses options sur `dev` flatte toujours le score. Le test scellé sert justement à voir la vraie performance avant la mise en production.

**Indices**
1. Lancez `atelier seuils` (ou `python exemples/04_balayer_les_seuils.py`).
2. Cherchez le seuil où `erreurs_pour_100` passe sous `5` tout en gardant au moins `50 %` automatisé.
3. Si vous voulez être plus prudent face au test scellé, montez légèrement le seuil (ex. `0,6` ou `0,7`).
