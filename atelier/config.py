# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Configuration de l'atelier lue depuis les variables d'environnement.

| Variable          | Valeurs                    | Défaut                                   |
|-------------------|----------------------------|------------------------------------------|
| WYAT_MODEL        | nom Hub ou dossier local   | teilomillet/wyat-1-800m                  |
| WYAT_BACKEND      | mlx, torch                 | mlx sur Mac Apple Silicon, torch ailleurs |
| WYAT_DEVICE       | auto, cpu, cuda, mps       | auto (cuda si visible, sinon cpu)        |
| WYAT_THREADS      | entier                     | choix de PyTorch                         |
| WYAT_MODE         | auto, rapide, complet      | auto (rapide sur torch + cpu)            |
| WYAT_PRECALCULE   | 0, 1                       | 0 (1 = rejoue les décisions livrées)     |
| WYAT_CACHE        | 0, 1                       | 1 (cache local des décisions)            |
| ATELIER_ANIMATEUR | 0, 1                       | 0 (1 = autorise le test scellé en CLI)   |
"""
from __future__ import annotations

import os
import platform
from pathlib import Path
from typing import Final, Literal

Backend = Literal["mlx", "torch"]

DEFAULT_MODEL: Final[str] = "teilomillet/wyat-1-800m"
RACINE: Final[Path] = Path(os.environ.get("ATELIER_RACINE", Path(__file__).resolve().parent.parent))
DATASET: Final[Path] = RACINE / "dataset"
DATASET_SECU: Final[Path] = DATASET / "securite"
PRECALCULE: Final[Path] = DATASET / "decisions_precalculees.jsonl"
CACHE_LOCAL: Final[Path] = RACINE / ".cache_atelier" / "decisions.jsonl"
MISSIONS: Final[Path] = RACINE / "missions"


def _bool_env(nom: str, defaut: bool = False) -> bool:
    """Lit un booléen (`0` / `1`) dans l'environnement."""
    valeur = os.environ.get(nom)
    if valeur is None:
        return defaut
    return valeur == "1"


def modele() -> str:
    """Identifiant Hugging Face ou chemin local du modèle."""
    return os.environ.get("WYAT_MODEL", DEFAULT_MODEL)


def mac_apple_silicon() -> bool:
    """Vrai sur macOS arm64 (Apple Silicon)."""
    return platform.system() == "Darwin" and platform.machine() == "arm64"


def backend() -> Backend:
    """Moteur d'inférence (`mlx` sur Mac Apple Silicon, `torch` ailleurs)."""
    choix = os.environ.get("WYAT_BACKEND")
    if choix in ("mlx", "torch"):
        return choix  # type: ignore[return-value]
    return "mlx" if mac_apple_silicon() else "torch"


def device() -> str:
    """Périphérique d'exécution (`gpu-apple`, `cuda`, `mps` ou `cpu`)."""
    if backend() == "mlx":
        return "gpu-apple"
    choix = os.environ.get("WYAT_DEVICE", "auto")
    if choix != "auto":
        return choix
    try:
        import torch
    except ImportError:
        return "cpu"
    return "cuda" if torch.cuda.is_available() else "cpu"


def threads() -> int | None:
    """Nombre explicite de threads CPU pour PyTorch, ou `None` (défaut)."""
    valeur = os.environ.get("WYAT_THREADS")
    return int(valeur) if valeur else None


def precalcule_seul() -> bool:
    """Vrai si l'atelier rejoue uniquement `dataset/decisions_precalculees.jsonl`."""
    return _bool_env("WYAT_PRECALCULE", defaut=False)


def cache_actif() -> bool:
    """Vrai si le cache disque `.cache_atelier/decisions.jsonl` est activé."""
    return _bool_env("WYAT_CACHE", defaut=True)


def mode_rapide() -> bool:
    """Mode rapide : jeux `dev` et `test` réduits (automatique sur PyTorch CPU)."""
    mode = os.environ.get("WYAT_MODE", "auto")
    if mode in ("rapide", "complet"):
        return mode == "rapide"
    return not precalcule_seul() and backend() == "torch" and device() == "cpu"


def animateur() -> bool:
    """Vrai si l'ouverture du test scellé est autorisée (`ATELIER_ANIMATEUR=1`)."""
    return _bool_env("ATELIER_ANIMATEUR", defaut=False)
