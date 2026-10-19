<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Matching the learner's level

Two independent axes:
- **Role**: decision-maker / HR / legal, developer, security. It sets the **content**, meaning the track and the cases (`missions/parcours.toml`).
- **Level**: Découverte / Praticien / Expert. It sets the **register**: words, depth, who types, pace.

Never ask "what's your level?". Infer it from what they say and, above all, from their **predictions**.

## Diagnose in the first five minutes

Ask one open question tied to their work: « Dans ton équipe, aujourd'hui, qui décide où va une demande, et comment ? » Then listen:

| Signal | Découverte | Praticien | Expert |
|---|---|---|---|
| Vocabulary | "l'IA", "le système", business words | "modèle", "précision", "API", "prompt" | "calibration", "fuite de données d'éval", "intervalle", "baseline" |
| First prediction (step 1) | "il va comprendre" / no idea | "il va choisir facturation" | "facturation, mais marge faible : deux intentions" |
| Reaction to a number | asks what it means | asks how it's computed | asks the denominator and the split |
| Terminal | hesitant, wants you to run it | comfortable | already opened the code |

If signals conflict, start one level **lower** and climb fast: it costs one sentence, while starting too high costs the learner.

## Adapt at each step

| Lever | Découverte | Praticien | Expert |
|---|---|---|---|
| Scene | full (person, moment, stake), in their sector | short, in their sector | one sentence, or skip to the data |
| Prediction | binary: « sûr ou pas sûr ? » | open: « que va-t-il choisir, avec quelle marge ? » | quantitative: « quelle marge ? quel taux sur dev ? » |
| Commands | you run them, show the output, explain each column | they type, you suggest | they write their own probe (`exemples/`, `import wyat`) |
| Concept naming | everyday words first, the term second, one analogy | term + one-line definition | precise term; link to the literature if they want |
| Outputs shown | 2 contrasting | 3–4 | the raw table (`--erreurs`, `--csv`) |
| Numbers | raw count + what one error means for them | counts, interval | counts, interval, paired comparison, what would invalidate it |
| Action | edit one line of a TOML with you | the full mission file | the mission, then a variation of their own (another case, another sector) |
| Check | « explique-le à un collègue en une phrase » | apply it to their decision | find a failure mode the workshop didn't show |

## Re-calibrate continuously

- **Up**: two correct predictions in a row, or they anticipate the next concept → shorten scenes, give them the keyboard, ask harder questions.
- **Down**: a guess, a silence, or "je ne sais pas" twice → back to the scene, one contrasting pair of outputs, a binary question.
- **Sideways**: a decision-maker who asks about code, or a developer who asks about governance → follow them for a few minutes, then come back to the path.
- Say it aloud when you change pace, and offer the alternative: « On peut aller plus vite, ou regarder le code derrière : tu préfères ? »

## By role: what lands

- **Décideurs / RH / juridique:** the threshold is a business choice (cost of an error vs cost of a review); what *never* to automate (no ranking of people, AI Act high-risk categories: check with legal); governance (sealed test, journal, drift); licences.
- **Développeurs:** `Request.choice / noul / score`, `decide`, `to_dict()`; words to the model, numbers and formats to code; integrations; where it fails (agent loops, code output prediction).
- **Sécurité:** asymmetric cost; defence in depth; local / air-gapped deployment; what an attacker would do (subtle injection passes); logging every decision.

## Group of mixed levels

Pair a Praticien with a Découverte at the keyboard; ask the prediction to the least experienced person first; give experts the "what would invalidate this?" question at the close of each step.
