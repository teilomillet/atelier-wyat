<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Données du bloc 6 (sécurité) — SYNTHÉTIQUES

Tout est **inventé** pour l'atelier : commandes, tâches, SMS, e-mails, expéditeurs, domaines. Les adresses IP sont dans les plages réservées à la documentation (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24). Aucune donnée réelle, aucun lien actif.
Générées par `scripts/construire_dataset_securite.py` (relancer pour tout reconstruire, graines fixes).

| Fichier | Contenu | Lignes |
|---|---|---|
| `tous_commandes.csv` | commandes proposées par un agent de code : `id, tache, commande, label (autoriser / demander / refuser), acceptable, difficulte, note` | 60 |
| `commandes_dev.csv` / `commandes_test_scelle.csv` | séparation stratifiée par étiquette (40 % dev, graine 11) | 24 / 36 |
| `tous_messages.csv` | SMS et e-mails : `id, canal, expediteur, message, label (frauduleux / legitime), difficulte, note` | 50 |
| `messages_dev.csv` / `messages_test_scelle.csv` | même séparation | 20 / 30 |
| `*_rapide.csv` | sous-ensembles stratifiés pour le mode rapide (graine 2026) | 12 / 18 commandes, 10 / 16 messages |

**Honnêteté.** Les règles écrites du garde-fou (`atelier/securite.py`, liste noire et liste blanche) ont été écrites **en connaissant ces données**, et les formulations de wyat ont été choisies sur dev. Le test scellé n'a servi qu'à mesurer, une fois. Sur vos propres commandes, les règles rateront d'autres choses : c'est pour ça qu'elles ne sont qu'une couche.
Étiquettes : « demander » = sans danger grave mais à faire valider (installation de paquets, `git push`) ; c'est la classe la plus discutable.
