<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Souveraineté, RGPD, AI Act, auditabilité

Ce que l'atelier montre, et ce qui reste à faire chez vous. Ce document n'est pas un avis juridique.

## 1. Souveraineté : 100 % local
- Le modèle tourne sur le portable ou le serveur (MLX sur Mac Apple Silicon, PyTorch sur processeur ailleurs). **Aucune donnée ne sort** pendant une décision : la bibliothèque `wyat` n'ouvre le réseau que pour télécharger le modèle, une fois (`wyat download`, vérification par empreinte SHA-256).
- Démonstration : le cas 25 coupe le réseau dans le processus avant de charger le modèle ; tout fonctionne. Procédure pour un réseau isolé : [`deploiement_hors_ligne.md`](deploiement_hors_ligne.md).
- Pas de compte, pas de clé d'API, pas de coût par appel.

## 2. RGPD
- Le traitement local réduit les transferts (pas de sous-traitant d'IA, pas de transfert hors UE). Il ne dispense pas du reste : **base légale** pour réutiliser de vrais messages comme données d'évaluation, minimisation, durée de conservation des journaux, information des personnes, registre des traitements, et une AIPD si le traitement le justifie.
- Les données de l'atelier sont **synthétiques**. Pour vos jeux dev / test : extraits anonymisés ou pseudonymisés, relus.
- Cas 09 : un modèle seul ne détecte pas fiablement les données personnelles (numéros de carte manqués) ; les **formats se détectent par le code**.

## 3. AI Act (règlement (UE) 2024/1689)
- La plupart des usages de l'atelier (router un ticket, trier des alertes, signaler un e-mail) ne relèvent pas des systèmes à haut risque, mais **la qualification dépend de l'usage, pas du modèle**. Les usages listés à l'annexe III (emploi et gestion des travailleurs, accès à des services essentiels publics ou privés comme le crédit, etc.) sont à haut risque : c'est pourquoi le cas 05 vérifie la complétude d'une candidature **sans trier ni noter les personnes**.
- Ce qu'apporte un modèle de décision pour les obligations de transparence, de journalisation et de contrôle humain : une sortie fermée, une **probabilité par option**, un seuil explicite, un humain pour les cas incertains, un journal par décision.
- Secteur public : une décision administrative individuelle prise sur le fondement d'un traitement algorithmique doit le mentionner et en expliquer les règles sur demande (code des relations entre le public et l'administration, art. L. 311-3-1). Le cas 18 réoriente une demande ; il ne décide pas d'un droit.

## 4. Auditabilité
- Chaque décision expose `probabilities_by_id`, `probability_margin`, `selected` et `model_id` (empreinte du modèle).
- Journal type (cas 14 et 21) : horodatage, empreinte du modèle, version de la politique (seuil), entrée ou référence, probabilités, action. Format JSONL, local, à verser dans votre SIEM ou votre archivage.
- Reproductibilité : mêmes entrées, même modèle, mêmes choix, probabilités identiques à quelques 1e-5 près entre MLX et PyTorch CPU (vérifié sur les cas 01 à 12 et les notebooks).
- Le **test scellé** (étape 5) est la pièce d'audit : on le rouvre à date fixe, options figées, et on vérifie que les chiffres tiennent.

## 5. Calibration et abstention
- Une probabilité n'est pas une garantie : mesurez-la (ECE, étape 5). Dans l'atelier, recalibrer sur 63 messages a **dégradé** le test (ECE 0,102 → 0,150).
- L'abstention se règle par un **seuil de marge** choisi sur dev selon le coût d'une erreur ; en sécurité, le seuil est bas (on dérange un humain plutôt que de laisser passer).

## 6. Coût et latence (mesurés le 19/10/2026)
| Machine | Chargement | Une décision (5 options, message court) | Mémoire |
|---|---|---|---|
| Mac M4 Pro, MLX | 2,5 à 4 s | 0,15 s | — |
| VM Linux 8 vCPU Xeon, PyTorch CPU | 8 à 14 s | 0,75 à 0,9 s | ≈ 5 Go (FP32) |
| Même VM limitée à 2 threads (portable ancien) | — | ≈ 2,1 s | ≈ 5 Go |

Un cas de la galerie s'exécute en 3 à 7 s sur Mac et 11 à 32 s sur Linux CPU, chargement compris. Coût marginal d'une décision : l'électricité de la machine.

## 7. Limites à annoncer
Voir [`benchmarks.md`](benchmarks.md) et les verdicts ❌ / ⚠️ de la galerie : priorités tassées vers le milieu (cas 17), injections subtiles non détectées (cas 16), destinataires et montants non vérifiés (cas 14), compréhension de code sous le hasard (cas 15), pilotage d'agent (cas 11). Les poids sont **non commerciaux** : [`licence_du_modele.md`](licence_du_modele.md).
