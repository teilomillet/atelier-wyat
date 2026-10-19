# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Ajouter une colonne « décision » à un tableau (export CSV / Excel de votre CRM, de vos tickets…)."""
import os
import platform

import pandas as pd
import wyat

modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")
OPTIONS = {"appeler": "Prospect prêt à acheter : besoin précis, entreprise identifiée, délai proche ou demande de rappel",
           "informer": "Intérêt réel mais pas de projet immédiat : envoyer de la documentation",
           "ecarter": "Pas un client potentiel : étudiant, démarchage, publicité ou hors sujet"}

df = pd.read_csv("cas_usage/06_qualification_leads/donnees.csv")          # ou pd.read_excel("export_crm.xlsx")
decisions = [modele.decide(wyat.Request.choice("Quelle suite donner à cette demande ?", OPTIONS, context=t)) for t in df.demande]
df["suite"] = [d.selected for d in decisions]
df["marge"] = [round(d.probability_margin, 2) for d in decisions]
df.to_csv("leads_qualifies.csv", index=False)                              # ou df.to_excel(...)
print(df[["demande", "suite", "marge"]].to_string(max_colwidth=50))
