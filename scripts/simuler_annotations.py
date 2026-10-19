# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Crée dataset/annotations_exemple_SIMULEES.csv (10 annotateurs FICTIFS, tirés au hasard)
et le gabarit vide dataset/annotations_atelier.csv à remplir pendant l'atelier.
Les annotations simulées ne viennent d'aucune personne réelle : elles servent à montrer les calculs."""
import csv
import random
from pathlib import Path

D = Path(__file__).resolve().parents[1] / "dataset"
CLASSES = ["facturation", "technique", "resiliation", "livraison", "autre"]
with open(D / "labeling_15_corrige.csv", encoding="utf-8") as _f:
    rows = list(csv.DictReader(_f))
rng = random.Random(7)
out = []
for r in rows:
    acc = r["labels_acceptables"].split("|")
    alts = [a for a in acc if a != r["label"]]
    line = {"numero": r["numero"]}
    for k in range(1, 11):
        u = rng.random()
        if r["difficulte"] == "facile":
            lab = r["label"] if u < 0.92 else rng.choice([c for c in CLASSES if c != r["label"]])
        else:
            lab = r["label"] if u < 0.55 else (rng.choice(alts) if alts and u < 0.9 else rng.choice(CLASSES))
        line[f"A{k}"] = lab
    out.append(line)
cols = ["numero"] + [f"A{k}" for k in range(1, 11)]
with open(D / "annotations_exemple_SIMULEES.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(out)
with open(D / "annotations_atelier.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows({"numero": r["numero"]} for r in rows)
print("ok")
