# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Évaluer des options sur dev : exactitude, intervalle de confiance, erreurs.

Lancer : .venv/bin/python exemples/03_evaluer_un_jeu.py [travail/options.toml]
"""
import sys

import atelier as at

options = at.lire_options(sys.argv[1]).options if len(sys.argv) > 1 else at.OPTIONS
modele = at.charger_modele()
dev = at.lire("dev")                                   # jamais le test scellé ici
rapport, res = at.evaluer(modele, dev, options)        # wyat.evaluation.evaluate, ligne par ligne
acc, bas, haut = at.intervalle_bootstrap(res.correct)
print(f"exactitude {acc:.1%}  IC 95 % [{bas:.1%} ; {haut:.1%}]  ECE {rapport.expected_calibration_error:.3f}")
print(res[~res.correct][["message", "label", "prediction", "marge"]].to_string(index=False))

# Le même calcul avec wyat seul :
# from wyat.evaluation import EvaluationCase, evaluate
# cas = [EvaluationCase(id=r.id, request=at.requete(r.message, options), expected=(r.label,)) for r in dev.itertuples()]
# print(evaluate(modele, cas).accuracy)
