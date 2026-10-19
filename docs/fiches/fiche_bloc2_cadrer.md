<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Bloc 2 — Cadrer la décision (fiche de travail, 20 min)

**Table n° ____ · Prénoms : ______________________________**

Situation : le service client de **Lumio** (opérateur fictif : box, mobile, TV, envoi de matériel) reçoit environ 2 000 messages par jour. Aujourd'hui, une personne lit chaque message pour l'envoyer à la bonne équipe. On veut qu'un modèle de décision fasse ce tri **quand il est sûr**, et qu'il **passe la main à un humain sinon**.

## 1. La question (une seule phrase, posée au modèle)
> Exemple : « Quel service doit traiter ce message client ? »

Notre question : ______________________________________________________________

## 2. Les options : liste **fermée**, une ligne par option
Règles :

- chaque option a un **identifiant court** (pour le code) et une **description** (pour le modèle) ;
- décrivez ce que l'option **couvre**, avec les **mots des clients** (« prélevé », « débité », « plus de réseau »…) ;
- **pas d'option « tout le reste / pas sûr »** : on traitera l'incertitude par une règle (étape 4) ;
- 3 à 7 options : au-delà, découpez en deux décisions.

| Identifiant | Description lue par le modèle (ce que ça couvre) | Action déclenchée (qui, quoi, en combien de temps) |
|---|---|---|
| facturation | | |
| technique | | |
| resiliation | | |
| livraison | | |
| autre | | |
| | | |

## 3. Cas limites : où va… ?
| Message | Option choisie | Pourquoi ? |
|---|---|---|
| « J'ai résilié en août et vous continuez de me prélever » | | |
| « Internet coupé depuis une semaine, je vais partir » | | |
| « Je déménage, comment transférer ma box ? » | | |
| « l'appli plante dès que j'ouvre mes factures » | | |
| « bonjour » | | |

Notre **règle d'annotation** pour les messages à plusieurs sujets (une phrase) :

_______________________________________________________________________________

## 4. Quand passer la main à un humain ?
- Coût d'une **erreur de tri** (client mal orienté) : ☐ faible ☐ moyen ☐ élevé — exemple : ______________________
- Coût d'un message **lu par un humain** : environ ____ minutes
- Part de messages qu'on voudrait **automatiser** : ____ %
- Nombre d'erreurs automatiques **acceptable** pour 100 messages : ____
- Toujours un humain, quelle que soit la confiance, pour : ☐ résiliation ☐ menace juridique ☐ décès ☐ autre : ______

## 5. Données
D'où viendraient nos exemples étiquetés ? ☐ vrais messages anonymisés (RGPD : base légale, minimisation, suppression des noms, numéros et IBAN) ☐ jeu public ☐ messages synthétiques (rapide, mais à relire, et ils ne ressemblent jamais tout à fait aux vrais)

Combien d'exemples pour le **dev** ? ____ Pour le **test scellé** ? ____ Qui garde le test sous clé ? ________
