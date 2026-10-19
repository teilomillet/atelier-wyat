# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Sous-ensembles « mode rapide » (PC sans GPU Apple) : dev 20 et test 25 messages.

Tirage stratifié et reproductible : on garde la proportion de chaque étiquette,
puis, dans chaque étiquette, la proportion de chaque difficulté (plus forts restes).
Le test réduit reste tiré du test scellé : il ne sert toujours qu'une fois.
Usage : python scripts/construire_sous_ensembles.py
"""
from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

DATASET = Path(__file__).resolve().parent.parent / "dataset"
TAILLES = {"dev.csv": ("dev_rapide.csv", 20), "test_scelle.csv": ("test_scelle_rapide.csv", 25)}
GRAINE = 2026


def repartir(effectifs: dict[str, int], total: int) -> dict[str, int]:
    """Répartit `total` proportionnellement aux effectifs (méthode des plus forts restes)."""
    n = sum(effectifs.values())
    bruts = {k: total * v / n for k, v in effectifs.items()}
    parts = {k: int(b) for k, b in bruts.items()}
    reste = total - sum(parts.values())
    for k in sorted(bruts, key=lambda k: (-(bruts[k] - parts[k]), k))[:reste]:
        parts[k] += 1
    return parts


def tirer(df: pd.DataFrame, total: int, rng: random.Random) -> pd.DataFrame:
    choisis = []
    par_label = repartir(df["label"].value_counts().to_dict(), total)
    for label in sorted(par_label):
        bloc = df[df["label"] == label]
        par_diff = repartir(bloc["difficulte"].value_counts().to_dict(), par_label[label])
        for diff in sorted(par_diff):
            ids = sorted(bloc[bloc["difficulte"] == diff]["id"])
            choisis += rng.sample(ids, par_diff[diff])
    return df[df["id"].isin(choisis)]  # garde l'ordre du fichier d'origine


if __name__ == "__main__":
    rng = random.Random(GRAINE)
    for source, (cible, taille) in TAILLES.items():
        df = pd.read_csv(DATASET / source, encoding="utf-8")
        sous = tirer(df, taille, rng)
        sous.to_csv(DATASET / cible, index=False, encoding="utf-8")
        print(cible, len(sous), sous["label"].value_counts().to_dict(), sous["difficulte"].value_counts().to_dict())
