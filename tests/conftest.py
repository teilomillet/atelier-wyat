# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Les tests tournent sans modèle : ils rejouent dataset/decisions_precalculees.jsonl (vraies décisions de wyat)."""
import os

os.environ["WYAT_PRECALCULE"] = "1"
os.environ["WYAT_MODE"] = "complet"
os.environ.pop("ATELIER_ANIMATEUR", None)

import pytest  # noqa: E402

import atelier as at  # noqa: E402


@pytest.fixture(scope="session")
def modele():
    return at.charger_modele(verbeux=False)
