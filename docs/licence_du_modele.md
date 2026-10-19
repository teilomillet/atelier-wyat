<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Licence des poids wyat-1-800m : évaluation ou production ?

**À lire avant tout projet.** Le contenu de ce dépôt (code, exercices, documentation, données) a sa propre licence (voir `LICENSE`). Le **modèle** wyat-1-800m, téléchargé à part, a la sienne.

## Ce que dit la licence du modèle (carte du modèle et `NOTICE`, vérifiées le 19/10/2026)

- **Adaptateurs et tête de décision entraînés par wyat** (`model/adapters.safetensors`, `model/head.safetensors`) : usage, copie et redistribution **non commerciaux** autorisés, à condition de conserver la mention et l'attribution du fichier `NOTICE`. **L'usage commercial n'est pas accordé** par cette publication (métadonnée Hugging Face : `license: other`, `license_name: wyat-non-commercial-distribution`).
- Code d'exécution (`runtime/`), modèle de base Qwen3.5-0.8B-Base et tokenizer : Apache-2.0.
- L'entraînement a utilisé, entre autres, des exemples adaptés de FalseReject (Amazon Science), sous licence CC BY-NC 4.0.
- Le modèle est fourni sans garantie ; il est décrit comme expérimental.

Sources : <https://huggingface.co/teilomillet/wyat-1-800m> (section « License ») et le fichier `NOTICE` du dépôt du modèle. La bibliothèque `wyat` sur PyPI est sous Apache-2.0 ; cela ne change pas la licence des poids.

## En pratique pour une entreprise ou une administration

| Usage | Avec les poids publiés |
|---|---|
| Suivre cet atelier, se former, comprendre les modèles de décision | possible : usage non commercial |
| Évaluer en interne sur des données fictives ou anonymisées, sans effet sur l'activité | probablement compatible ; **faites valider par votre service juridique**, la notion de « non commercial » n'est pas définie dans la publication |
| Mettre en production (trier de vrais tickets, alertes, courriers, dans un processus de l'organisation) | **non accordé** par la licence publiée : il faut un accord écrit avec l'auteur |
| Intégrer le modèle dans un produit ou un service vendu | **non accordé** |
| Redistribuer les poids (clé USB, miroir interne) | possible dans un cadre non commercial, avec `LICENSE` et `NOTICE` |

Ce tableau est une lecture pratique, pas un avis juridique. En cas de doute, la licence du modèle prime.

**Pour un usage en production** : licence commerciale ou modèle de décision sur mesure, voir la section « Et après ? » du `README.md`. D'autres modèles de décision existent (vérifiez leur licence au cas par cas) : la méthode de l'atelier (cadrer, mesurer, seuil, journal) s'applique à tout modèle de décision.
