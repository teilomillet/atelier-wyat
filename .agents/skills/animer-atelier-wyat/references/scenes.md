<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Scènes, étape par étape

Each step: a **scene** to transpose to the learner's sector, the **prediction** to ask for, **what to run**, the **one question**, the expected answer, the **word** to name, the **action**, and how to **close**. Each `missions/N_*/MISSION.md` opens with a **Situation**: that text is the base scene, and the seeds below only help you transpose and pace it. Recorded numbers are in `docs/guide_animateur.md` (section named per step). Run the commands to show real outputs; don't recite numbers from the guide before running them. **Never quote a sealed-test number before the corresponding `--final`** (AGENTS.md §5).

Characters are roles (« la conseillère », « le chef de quart »), never real names of the learner's colleagues. Default sector transpositions are given; invent others in the same spirit.

| Secteur | Personne | File / flux qui déborde |
|---|---|---|
| Banque | conseillère en agence, analyste conformité | messages clients, alertes KYC, demandes de changement de RIB |
| Secteur public | agent d'accueil d'une collectivité, rapporteur | demandes d'usagers, contributions à une consultation |
| Énergie / industrie | chef de quart, technicien de maintenance | demandes d'intervention, alertes IT/OT |
| Luxe / commerce | responsable service client, protection de la marque | avis clients FR/EN, annonces de places de marché |
| Défense / souverain | officier de permanence, analyste sur réseau isolé | documents à classer, journaux d'accès |
| Tech | ingénieur d'astreinte, équipe plateforme | tickets, commandes proposées par un agent IA |

---

## Étape 1 — Une première décision (niveau 1 · Guide « Bloc 1 »)

**Scène.** Lundi, 8 h 10. *[La conseillère / l'agent d'accueil…]* ouvre sa file : 400 messages depuis vendredi. Le premier attend depuis jeudi dans « autre » : « On m'a prélevé deux fois ce mois-ci, vous pouvez me rembourser ? ». Elle le range en une demi-seconde. Sa responsable : « Il nous faudrait ce réflexe-là, en machine. Sans envoyer nos messages chez quelqu'un d'autre. »
**Prédire.** « Elle a *rédigé* une réponse, ou *choisi* dans une liste ? » Puis : « Une règle par mots-clés ferait-elle aussi bien ? »
**Lancer.** `python exemples/00_natif_contre_wyat.py` (natif contre wyat, mêmes messages de dev) ; puis `atelier decider "J'ai résilié en août et vous continuez de me prélever !!!"` et `atelier decider "bonjour"`.
**Question.** « Les deux se trompent parfois. Lequel des deux peut dire qu'il n'est *pas sûr* ? Regarde la marge du message à deux sujets. »
**Attendu.** Le natif ne doute jamais ; wyat a une marge faible sur le message à deux sujets… et une marge forte sur « bonjour ».
**Nommer.** **Modèle de décision** (il *choisit* parmi des options fermées) ; **marge** = probabilité du 1er − celle du 2e.
**Agir.** Étape 1, `travail/mission1.toml`, puis `atelier verifier 1`.
**Clore.** « Sur dev, combien pour les mots-clés, combien pour wyat ? » (compte brut). Rappeler que les options ont été écrites en regardant dev : ce chiffre flatte wyat. « bonjour » reste en suspens : on y revient au niveau 4.

## Étape 2 — Cadrer (niveau 2 · Guide « Bloc 2 »)

**Scène.** Lundi, 10 h. La responsable demande à trois collègues comment ils rangent les messages. L'un dit « compta », l'autre « paiements », le troisième « réclamations ». Et « J'ai résilié et vous me prélevez encore », c'est quoi ?
**Prédire.** « Si on donne au modèle trois mots, "compta / paiements / réclamations", que va-t-il faire de ce message ? »
**Lancer.** Rien au début : `docs/fiches/fiche_bloc2_cadrer.md` (question, options fermées, action de chaque option), à l'écran ou sur papier.
**Question.** « Une option "autre / pas sûr" réglerait le problème ? »
**Attendu.** Non : elle ressemble à tout, elle aspire (on le verra au niveau 2 avec le fourre-tout). L'incertitude se gère par une **règle sur la marge**, pas par une option.
**Nommer.** **Options fermées**, **une action par option**, les trois formes : Choice (une parmi N), Noul (oui / non), Score (échelle).
**Agir.** Étape 2, `travail/cadrage.toml`, `atelier verifier 2` (sans modèle).
**Clore.** « Quel cas doit *toujours* aller à un humain, même si le modèle est sûr ? » (décès, menace juridique…). Noter leur réponse : elle servira au seuil.

## Étape 4 — Le libellé est la définition (niveau 2, suite · Guide « Bloc 4 »)

**Scène.** Mardi. Un collègue a « simplifié » les options pour qu'elles tiennent sur une ligne : la facturation ne parle plus des prélèvements.
**Prédire.** « Ça change quoi, d'enlever deux mots ? »
**Lancer.** `atelier evaluer --erreurs` avec les options de départ de l'étape 4 (`travail/options.toml`), puis avec les options de référence.
**Question.** « Regarde les messages mal rangés : quels mots emploient-ils ? Sont-ils dans l'option ? »
**Attendu.** « prélèvement », « débit » ; l'option ne les dit plus, donc le modèle ne peut pas les rattacher.
**Nommer.** **Le libellé d'une option est sa définition** : le modèle ne connaît que ce texte.
**Agir.** Étape 4 : réécrire l'option dans `travail/options.toml`, `atelier verifier 4` (dev).
**Clore.** Le gain en compte brut sur dev. Puis : « Et sur des messages qu'on n'a jamais vus ? » On ne sait pas encore. C'est le niveau 3.

## Étape 3 — Données et accord (niveau 3 · Guide « Bloc 3 »)

**Scène.** Mercredi, salle de pause. La responsable a donné les 15 mêmes messages à trois collègues. Sur « internet coupe tout le temps, je vais finir par résilier », l'un a mis technique, l'autre résiliation. Le troisième : « Si nous trois on n'est pas d'accord, la machine aura "raison" par rapport à qui ? »
**Prédire.** « Sur ces 15 messages, à quel point penses-tu tomber d'accord avec moi ? »
**Lancer.** Le ou la participant·e annote `docs/fiches/fiche_bloc3_annotation.md`. Seul·e : **tu annotes de ton côté, sans voir ses réponses ni le corrigé** (AGENTS.md §3). Puis `atelier accord travail/annotations.csv`.
**Question.** « Deux personnes qui cochent au hasard une case sur 5, à quelle fréquence tombent-elles d'accord ? »
**Attendu.** Environ 1 fois sur 5, plus si tout le monde coche la même case. Il faut donc corriger l'accord brut du hasard.
**Nommer.** **Accord inter-annotateurs (κ)**. Les désaccords tombent sur les messages ambigus : ce sont ceux qu'on enverra à un humain.
**Deuxième question.** « Si je réécris mes options jusqu'à 100 % sur ces messages, que vaut ce 100 % lundi prochain ? » → **dev** pour régler, **test scellé** pour juger, ouvert une fois. Puis `atelier evaluer` (dev) : intervalle de confiance, calibration (ECE).
**Agir.** `atelier verifier 3`.
**Clore.** « Où un humain et une IA n'ont-ils pas été d'accord, et qui avait raison ? »

## Étape 5 — Politique et test scellé (niveau 4 · Guide « Bloc 5 », sans ses chiffres du test)

**Scène.** Jeudi. La directrice des opérations demande : « On automatise combien ? Et combien d'erreurs je dois accepter ? » La conformité ajoute : « Et vous me prouvez ça comment ? »
**Prédire.** « Les erreurs de wyat, elles ont des marges fortes ou faibles ? »
**Lancer.** `atelier seuils` (dev) : pour chaque seuil, la part automatisée et les erreurs.
**Question.** « Combien coûte une erreur de tri chez toi ? Combien coûte une relecture ? » Puis : « Alors, quel seuil ? »
**Attendu.** Ni tout ni rien : un seuil, choisi selon le coût. Sous le seuil, un humain décide.
**Nommer.** **Seuil**, **politique de décision**, **abstention / humain dans la boucle**.
**Agir.** Étape 5, `travail/politique.toml` (seuil + tolérance), `atelier verifier 5` (dev).
**Climax (une seule fois).** « On fige tout : options et seuil. Plus de retouche après. Ton pronostic sur des messages jamais vus ? » Noter le pronostic dans le journal. Puis, devant la personne : `ATELIER_ANIMATEUR=1 atelier verifier 4 --final`, puis `… verifier 5 --final`. Lire le résultat ensemble, critère par critère.
**Clore.** « Pourquoi le test est-il moins bon que dev ? » → les options ont été écrites en regardant dev ; peu de messages. **Dev flattait ; le critère n'a pas menti.** Ensuite seulement : le notebook bloc 5 en débrief (calibration ajustée sur dev, confirmée sur le test). On peut alors revenir à « bonjour », et à la comparaison natif / wyat sur le test (AGENTS.md §4.3).

## Étape 6 — Garde-fou de sécurité (piste Sécurité · Guide « Bloc 6 »)

**Scène.** Vendredi, 17 h 40. Un agent de code IA propose une commande pour « libérer de la place » sur un serveur. Au même moment, une cliente âgée reçoit un SMS « de sa banque » qui lui demande de confirmer un virement.
**Prédire.** « Parmi ces commandes, lesquelles te font peur ? Le modèle sera-t-il d'accord ? »
**Lancer.** `atelier securite commande "…" --tache "…"` sur quelques commandes (sections 1–2 du notebook bloc 6 seulement : la suite ouvre le test scellé), `python exemples/05_garde_fou.py`, `atelier securite message …`.
**Question.** « Une validation de trop coûte 10 secondes ; une commande dangereuse autorisée peut coûter le serveur. Quel seuil ? »
**Attendu.** Celui qui ne laisse passer aucune dangereuse, quitte à déranger un humain plus souvent.
**Nommer.** **Coût asymétrique** ; puis, après le `--final` : **défense en profondeur** (règles + wyat + vérifications + humain : aucune couche ne suffit seule).
**Agir.** Étape 6, `travail/securite.toml` (ou `travail/garde.py`), `atelier verifier 6` ; réglage figé, une fois : `ATELIER_ANIMATEUR=1 atelier verifier 6 --final`.
**Clore.** Une limite assumée : l'injection subtile passe. Pour un développeur ou un RSSI : `integrations/garde_http.py`, `integrations/hook_claude_code.py`, cas 13 à 17, 19, 25.

## Étape 7 — Votre cas (pistes Décideurs / Développeurs · Guide « Cas par secteur »)

**Scène.** Trois mois plus tard, à la machine à café de *leur* organisation. Un collègue : « Vous pourriez faire pareil pour… ? »
**Prédire.** « Dans ton service, quelle décision ressemble à celle de ce matin : fréquente, à options fermées, avec une action claire ? »
**Lancer.** Un cas de leur secteur (banque 20 / 21, public 18 / 26, industrie 22, luxe 23 / 24, défense 25, tech 14 / 15) : `python cas_usage/<cas>/cas.py`. Montrer son verdict ✅ / ⚠️ / ❌.
**Question.** « Change **une** option pour ton organisation et relance. Qu'est-ce qui a changé ? » Puis : « Quel cas ne marche pas, et pourquoi ? »
**Attendu.** Comprendre une situation ou compter, ce n'est pas choisir dans une liste ; les montants, destinataires et formats vont **au code**.
**Nommer.** La recette : une décision, des options écrites, des exemples sur lesquels on s'est mis d'accord, un test scellé, un seuil choisi selon le coût, un journal. **Le modèle n'est qu'une pièce.**
**Agir.** `missions/7_votre_cas/MISSION.md` : question + options fermées + action par option + seuil + contrôles en code, dans `travail/mon_cas.toml`.
**Clore.** `docs/conformite.md` et `docs/licence_du_modele.md` (poids non commerciaux). Puis, une fois et seulement si c'est pertinent : l'auteur construit des modèles de décision sur les données de l'organisation (AGENTS.md §7).
