<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# 26 petits cas d'usage prêts à lancer

Chaque dossier contient **un script de 20 à 40 lignes** (`cas.py`), un petit fichier `donnees.csv` et la **vraie sortie du modèle** (`sortie_mlx.txt`). On montre aussi bien ce qui marche du premier coup (✅) que ce qui demande du code autour (⚠️) ou ce qu'il ne faut pas confier au modèle seul (❌).

```sh
.venv/bin/python cas_usage/01_tri_support/cas.py                 # lancer un cas (≈ 4 s sur Mac)
.venv/bin/python cas_usage/18_reorientation_usagers/cas.py       # voir le cas naïf vs cadré avec wyat
```

*Rappel des 3 types de questions `wyat` : **`Choice`** = choisir parmi une liste d'options · **`Noul`** = répondre oui ou non (`probability_true`) · **`Score`** = noter sur une échelle ordonnée.*

| # | Cas | Secteur | Type | Sécurité | Résultat réel | Verdict |
|---|---|---|---|---|---|---|
| 01 | [Trier les messages du support (boutique en ligne)](01_tri_support/README.md) | Commerce | Choice |  | 12/12 choix justes ; 3 message(s) pour un humain → routage.csv | ✅ à montrer |
| 02 | [Router les courriers et documents entrants](02_routage_courrier/README.md) | Tous | Choice |  | 12/12 documents bien routés | ✅ à montrer |
| 03 | [Contrôler les notes de frais](03_notes_de_frais/README.md) | Tous | Choice + Noul + code |  | ecriture : 12/12 justes ; verification : 3/3 justes | ✅ à montrer (version wyat + code) |
| 04 | [Relire les clauses d'un contrat fournisseur](04_clauses_contrat/README.md) | Tous | Choice (plusieurs questions sur un document) |  | ecriture : 12/12 cases justes ; verification : 7/8 cases justes | ✅ à montrer |
| 05 | [Vérifier qu'une candidature est complète (pas de tri des personnes)](05_dossier_candidature/README.md) | Tous | Noul (3 questions) |  | ecriture : 17/18 pièces bien détectées ; verification : 9/9 pièces bien détectées | ✅ à montrer |
| 06 | [Qualifier les demandes de contact commerciales](06_qualification_leads/README.md) | Commerce | Choice |  | ecriture : 6/8 demandes bien qualifiées ; verification : 1/3 demandes bien qualifiées | ⚠️ faible : 7/11 au total |
| 07 | [Modérer les avis clients avant publication](07_moderation_avis/README.md) | Commerce | Choice |  | ecriture : 9/10 avis bien traités ; verification : 3/3 avis bien traités | ✅ à montrer |
| 08 | [Donner une priorité aux alertes d'exploitation](08_priorite_incident/README.md) | Tech | Score (P4 → P1) |  | 7/10 priorités exactes, 9/10 à un niveau près | ⚠️ moyen (bon à un niveau près) |
| 09 | [Avant d'envoyer un mail à l'extérieur : données personnelles ?](09_rgpd_mail_sortant/README.md) | Tous | Noul + règles | oui | ecriture : wyat seul 9/10, wyat + règles 10/10 ; verification : wyat seul 1/3, wyat + règles 2/3 | ⚠️ limite : utile seulement avec les règles |
| 10 | [Assistant documentaire : passage pertinent ? réponse appuyée par la source ?](10_rag_source/README.md) | Tech | Noul (2 questions) |  | passage pertinent : 7/8 justes ; réponse appuyée par la source : 6/8 justes | ⚠️ limite |
| 11 | [Piloter la boucle d'un agent : répondre, outil, demander, arrêter](11_boucle_agent/README.md) | Tech | Choice |  | 4/8 étapes justes | ❌ limite (à ne pas utiliser) |
| 12 | [Sécurité : garde-fou des commandes d'un agent, alerte sur les SMS / e-mails suspects](12_garde_et_arnaques/README.md) | Tech | Choice + Noul + règles | oui | 10/10 décisions de sécurité justes | ✅ à montrer (voir bloc 6 pour les vrais chiffres) |
| 13 | [Hameçonnage : premier tri des e-mails signalés](13_hameconnage_mails/README.md) | Tous | Noul + règles | oui | ecriture 8/8 ; verification 3/4 ; 0 e-mail(s) en zone grise pour l'analyste | ✅ à montrer (premier filtre) |
| 14 | [Contrôle des appels d'outils d'un agent IA avant exécution](14_appels_outils_agent/README.md) | Tech | Noul + table de code + journal | oui | 10/12 décisions conformes à la politique ; journal : cas_usage/14_appels_outils_agent/journal_appels.jsonl | ⚠️ utile seulement avec le code et la confirmation |
| 15 | [Garde-fou pour du code généré avant exécution](15_garde_code_genere/README.md) | Tech | Noul + règles | oui | ecriture : wyat seul 6/8, wyat + règles 6/8 ; verification : wyat seul 3/4, wyat + règles 3/4 | ⚠️ filet prudent, beaucoup de fausses alertes |
| 16 | [Signaler les entrées suspectes avant qu'un assistant IA ne les lise](16_injection_entrees/README.md) | Tech | Noul + règle | oui | ecriture : wyat seul 7/8, wyat + règle 7/8 ; verification : wyat seul 2/4, wyat + règle 2/4 | ⚠️ limite : seulement l'évident |
| 17 | [Prioriser les alertes de sécurité (IT et OT) de P4 à P1](17_priorite_alertes_securite/README.md) | Énergie / industrie, tech | Score (P4 → P1) + règles SOC/OT | oui | Modèle seul : 4/10 exacts (MAE 0.254, astreintes P1 0/3) ; wyat + règles SOC/OT : 7/10 exacts (astreintes P1 3/3) | ⚠️ seulement avec règles SOC/OT (tassé seul) |
| 18 | [Collectivité : la demande relève-t-elle de la mairie ou d'un autre organisme ?](18_reorientation_usagers/README.md) | Secteur public | Noul négatif vs Choice explicite |  | Question négative (Noul puis Choice) : 7/12 justes ; Choice avec périmètre explicite de la mairie : 12/12 justes (0 vers l'accueil) | ✅ à montrer (7/12 naïf → 12/12 cadré) |
| 19 | [Demandes d'accès privilégié : conditions remplies ?](19_conditions_acces_privilegie/README.md) | Banque, défense, tech | Score seul vs wyat + contrôles de champs | oui | Score seul sur texte libre : 3/10 décomptes exacts ; wyat + contrôles de champs : 10/10 exacts | ⚠️ avec champs structurés / code (3/10 seul) |
| 20 | [Fil d'échanges fournisseur : quelle est la demande actuelle ? (fraude au changement de RIB)](20_demande_modifiee_virement/README.md) | Banque, tous secteurs | Choice | oui | 10/10 demandes actuelles identifiées | ✅ à montrer |
| 21 | [Banque : pré-tri des alertes KYC / LCB-FT](21_alertes_kyc/README.md) | Banque | Choice + journal | oui | 9/10 alertes bien pré-triées ; journal (probabilité par option) : cas_usage/21_alertes_kyc/journal_kyc.jsonl | ✅ à montrer (avec repli humain) |
| 22 | [Industrie / énergie : router la maintenance et repérer les risques HSE](22_maintenance_et_hse/README.md) | Énergie / industrie | Choice + Noul |  | métier 10/10 ; signal HSE 10/10 | ✅ à montrer |
| 23 | [Avis clients (FR / EN) : aspects cités et tonalité](23_avis_clients_aspects/README.md) | Luxe / commerce | Choice (un par aspect) |  | F1 moyen par avis : 65.0 sur 100 | ⚠️ moyen (sur-étiquette) |
| 24 | [Protection de la marque : annonces de places de marché](24_surveillance_annonces/README.md) | Luxe / commerce | Choice + règles prix/mots |  | Contexte naïf (prix dans le prompt) : 3/8 relations justes ; texte seul (wyat) + prix/mots en code : 6/8 relations justes | ✅ wyat (texte) + règles (prix/mots) |
| 25 | [Environnement isolé : niveau de manipulation d'un document](25_documents_hors_ligne/README.md) | Défense / souverain | Choice, réseau coupé | oui | 6/10 niveaux proposés justes ; aucune connexion réseau n'a été possible pendant l'exécution | ⚠️ aide au tri seulement |
| 26 | [Consultation ou comité : quel énoncé de synthèse est le plus fidèle ?](26_synthese_consultation/README.md) | Secteur public, direction | Choice |  | 4/5 ; le rapporteur relit toujours : c'est une suggestion d'ordre, pas une synthèse | ⚠️ aide au rapporteur |

## Ce qu'on retient en parcourant les 26 scripts

- **Les mots à `wyat`, les chiffres et les règles au code** : dès qu'il y a un montant, une date, un IBAN ou un domaine e-mail, vérifiez-le avec un `if` en Python et laissez la phrase à `wyat` (cas 03, 09, 14, 17, 19, 24).
- **Décrire les options plutôt que poser une question négative** : remplacer un oui/non flou par un `Choice` explicite fait passer le cas 18 de `7/12` à `12/12`.
- **Utiliser la marge pour passer la main** : le modèle n'a pas besoin d'avoir toujours raison s'il envoie ses doutes à un humain.
