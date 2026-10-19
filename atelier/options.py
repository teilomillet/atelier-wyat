# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Options de référence (le « contrat » lu par le modèle) et lecture des fichiers TOML.

Format TOML (voir `missions/`) ::

    question = "Quel service doit traiter ce message client ?"   # facultatif
    [options]
    facturation = "Facturation et paiements : ..."
    technique = "..."
    [actions]            # facultatif (étape 2) : ce que fait le code pour chaque option
    facturation = "File Compta, réponse sous 48 h"
"""
from __future__ import annotations

import json
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

QUESTION: Final[str] = "Quel service doit traiter ce message client ?"

OPTIONS: Final[dict[str, str]] = {
    "facturation": (
        "Facturation et paiements : montant d'une facture, débits ou prélèvements bancaires, "
        "remboursement, moyen ou date de paiement"
    ),
    "technique": (
        "Problème technique : internet, wifi, box, TV, réseau mobile, carte SIM "
        "ou application qui ne fonctionne pas correctement"
    ),
    "resiliation": "Résiliation : le client veut mettre fin à son contrat, à une ligne ou à une option",
    "livraison": "Livraison et retours : commande, colis, suivi, réception ou renvoi d'un équipement",
    "autre": (
        "Autre demande précise : changement d'offre, déménagement, coordonnées, "
        "réclamation sur le service client, information générale"
    ),
}
SERVICES: Final[tuple[str, ...]] = tuple(OPTIONS)

#: Variante de l'exercice (étape 4) : la facturation ne parle plus des débits / prélèvements.
OPTIONS_EXERCICE: Final[dict[str, str]] = {
    **OPTIONS,
    "facturation": "Facturation : questions sur les factures",
}

#: Contre-exemple : libellés d'un mot + une option attrape-tout.
OPTIONS_FOURRE_TOUT: Final[dict[str, str]] = {
    "facturation": "Facturation",
    "technique": "Technique",
    "resiliation": "Résiliation",
    "livraison": "Livraison",
    "autre": "Autre, pas sûr, tout le reste",
}


@dataclass(frozen=True, slots=True)
class FichierOptions:
    """Contrat d'options validé lu depuis un fichier TOML."""

    question: str
    options: dict[str, str]
    actions: dict[str, str] = field(default_factory=dict)
    brut: dict[str, Any] = field(default_factory=dict)


def lire_options(chemin: str | Path) -> FichierOptions:
    """Parse et valide un fichier d'options TOML (`ValueError` explicite en cas d'erreur)."""
    cible = Path(chemin)
    try:
        texte = cible.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ValueError(f"Fichier introuvable : {cible}") from None

    try:
        brut = tomllib.loads(texte)
    except tomllib.TOMLDecodeError as erreur:
        raise ValueError(f"{cible} n'est pas un TOML valide : {erreur}") from None

    options = brut.get("options")
    if not isinstance(options, dict) or len(options) < 2:
        raise ValueError(f"{cible} : il faut une table [options] avec au moins deux options.")

    for cle, description in options.items():
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"{cible} : l'option « {cle} » doit avoir une description non vide.")

    actions_brutes = brut.get("actions", {})
    actions = {str(k): str(v) for k, v in actions_brutes.items()} if isinstance(actions_brutes, dict) else {}
    question = str(brut.get("question", QUESTION))
    return FichierOptions(
        question=question,
        options={str(k): str(v) for k, v in options.items()},
        actions=actions,
        brut=brut,
    )


def ecrire_options(chemin: str | Path, options: Mapping[str, str], question: str = QUESTION) -> None:
    """Écrit un fichier d'options TOML valide."""
    lignes = [f"question = {json.dumps(question, ensure_ascii=False)}", "", "[options]"]
    lignes.extend(f"{cle} = {json.dumps(val, ensure_ascii=False)}" for cle, val in options.items())
    Path(chemin).write_text("\n".join(lignes) + "\n", encoding="utf-8")
