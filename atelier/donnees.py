# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Lecture des jeux de données (support client et sécurité), avec gestion du mode rapide."""
from __future__ import annotations

from typing import Final

import pandas as pd

from . import config

SOUS_ENSEMBLES: Final[dict[str, str]] = {
    "dev.csv": "dev_rapide.csv",
    "test_scelle.csv": "test_scelle_rapide.csv",
}
JEUX: Final[dict[str, str]] = {
    "dev": "dev.csv",
    "test": "test_scelle.csv",
    "labeling": "labeling_15_corrige.csv",
    "tous": "tous_les_messages.csv",
}


def lire(nom: str, verbeux: bool = True) -> pd.DataFrame:
    """Lit `dataset/<nom>` (ou l'alias `dev`, `test`, `labeling`, `tous`).

    En mode rapide, `dev.csv` et `test_scelle.csv` sont remplacés par leur version réduite.
    """
    fichier = JEUX.get(nom, nom)
    if config.mode_rapide() and fichier in SOUS_ENSEMBLES:
        reduit = SOUS_ENSEMBLES[fichier]
        if verbeux:
            print(f"(mode rapide : {reduit} au lieu de {fichier})")
        fichier = reduit
    return pd.read_csv(config.DATASET / fichier, encoding="utf-8").fillna("")


def lire_secu(nom: str, verbeux: bool = True) -> pd.DataFrame:
    """Lit `dataset/securite/<nom>` (version `_rapide` en mode rapide pour `_dev` et `_test_scelle`)."""
    fichier = nom
    if config.mode_rapide() and fichier.endswith(("_dev.csv", "_test_scelle.csv")):
        reduit = fichier.replace(".csv", "_rapide.csv")
        if verbeux:
            print(f"(mode rapide : {reduit} au lieu de {fichier})")
        fichier = reduit
    return pd.read_csv(config.DATASET_SECU / fichier, encoding="utf-8").fillna("")
