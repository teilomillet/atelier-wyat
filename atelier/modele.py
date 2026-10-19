# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Chargement du modèle, cache disque des décisions et mode secours pré-calculé.

Toutes les décisions viennent du vrai modèle `wyat` (ou d'un fichier de décisions déjà
calculées par lui) : `ModeleAtelier` n'invente rien, il évite seulement de recalculer
ce qui l'a déjà été sur cette machine.
"""
from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Protocol

import pandas as pd
import wyat

from . import config
from .options import OPTIONS, QUESTION


class Decideur(Protocol):
    """Interface minimale partagée par `wyat.Model`, `ModeleAtelier` et `_AvecBarre`."""

    model_id: str

    def decide(self, requete_: wyat.Request, temperature: float | None = None) -> wyat.Decision:
        ...


def _cle(modele_id: str, requete_: wyat.Request) -> str:
    return hashlib.sha256(f"{modele_id}|{requete_!r}".encode("utf-8")).hexdigest()


def _lire_jsonl(chemin: Path) -> dict[str, wyat.Decision]:
    if not chemin.exists():
        return {}
    decisions: dict[str, wyat.Decision] = {}
    with chemin.open(encoding="utf-8") as fichier:
        for ligne in fichier:
            texte = ligne.strip()
            if not texte:
                continue
            entree = json.loads(texte)
            decisions[entree["cle"]] = wyat.Decision(
                entree["model_id"],
                tuple(entree["scores"]),
                tuple(entree["probabilities"]),
                tuple(entree["ranking"]),
            )
    return decisions


class DecisionNonPrecalculee(RuntimeError):
    """Mode secours : la requête demandée n'est pas dans le fichier pré-calculé."""


class ModeleAtelier:
    """Enveloppe autour de `wyat.Model` ajoutant un cache disque et un mode secours."""

    def __init__(
        self,
        modele: wyat.Model | None = None,
        rejeu: dict[str, wyat.Decision] | None = None,
        model_id: str | None = None,
    ) -> None:
        self._modele = modele
        self.model_id: str = modele.model_id if modele is not None else (model_id or "?")
        self._rejeu: dict[str, wyat.Decision] = rejeu or {}
        self._cache: dict[str, wyat.Decision] = (
            _lire_jsonl(config.CACHE_LOCAL) if (config.cache_actif() and modele is not None) else {}
        )
        self.secondes_par_message: float | None = None
        self.calculs: int = 0

    @property
    def secours(self) -> bool:
        return self._modele is None

    def decide(self, requete_: wyat.Request, temperature: float | None = None) -> wyat.Decision:
        cle = _cle(self.model_id, requete_)
        if temperature is None and cle in self._cache:
            return self._cache[cle]
        if temperature is None and self._modele is None:
            if cle in self._rejeu:
                return self._rejeu[cle]
            raise DecisionNonPrecalculee(
                "Mode secours (WYAT_PRECALCULE=1) : ce message ou ces options n'ont pas été "
                "pré-calculés. Gardez les options d'origine, ou lancez le modèle."
            )
        if self._modele is None:
            raise DecisionNonPrecalculee("Mode secours : la température n'est disponible qu'avec le modèle chargé.")

        decision = self._modele.decide(requete_, temperature=temperature)
        self.calculs += 1
        if temperature is None and config.cache_actif():
            self._cache[cle] = decision
            config.CACHE_LOCAL.parent.mkdir(parents=True, exist_ok=True)
            with config.CACHE_LOCAL.open("a", encoding="utf-8") as fichier:
                fichier.write(json.dumps({"cle": cle, **decision.to_dict()}, ensure_ascii=False) + "\n")
        return decision

    def en_cache(self, requete_: wyat.Request) -> bool:
        cle = _cle(self.model_id, requete_)
        return cle in self._cache or (self._modele is None and cle in self._rejeu)


def charger_modele(verbeux: bool = True) -> ModeleAtelier:
    """Charge `wyat-1-800m` avec le bon moteur (MLX, PyTorch CPU ou CUDA), ou le secours pré-calculé."""
    if config.precalcule_seul():
        rejeu = _lire_jsonl(config.PRECALCULE)
        ids = {d.model_id for d in rejeu.values()}
        modele = ModeleAtelier(rejeu=rejeu, model_id=ids.pop() if len(ids) == 1 else "?")
        if verbeux:
            print(f"MODE SECOURS : {len(rejeu)} décisions pré-calculées rejouées, modèle non chargé.")
        return modele

    debut = time.perf_counter()
    if config.backend() == "mlx":
        brut = wyat.load(config.modele(), backend="mlx")
    else:
        nb_threads = config.threads()
        if nb_threads:
            import torch

            torch.set_num_threads(nb_threads)
        brut = wyat.load(config.modele(), device=config.device())
    duree_chargement = time.perf_counter() - debut

    modele = ModeleAtelier(brut)
    essai = requete("Bonjour, ma box ne s'allume plus depuis ce matin, que faire ?", OPTIONS)
    brut.decide(essai)
    debut = time.perf_counter()
    brut.decide(essai)
    modele.secondes_par_message = time.perf_counter() - debut

    if verbeux:
        infos = f"backend={config.backend()}, device={config.device()}"
        if config.backend() == "torch":
            import torch

            infos += f", threads={torch.get_num_threads()}"
        print(f"Modèle chargé en {duree_chargement:.1f} s  ({infos}, id={modele_id(modele)})")
        print(f"Vitesse mesurée : ≈ {modele.secondes_par_message:.2f} s par message.")
        if config.mode_rapide():
            print("Mode RAPIDE (processeur seul) : jeux dev et test réduits.")
    return modele


def modele_id(modele: object) -> str:
    return str(getattr(modele, "model_id", "?"))[:24] + "…"


def duree_estimee(modele: object, n: int) -> str:
    secondes = getattr(modele, "secondes_par_message", None)
    if not secondes:
        return ""
    total = n * secondes
    return f"≈ {total:.0f} s" if total < 90 else f"≈ {total / 60:.1f} min"


def requete(
    message: str,
    options: Mapping[str, str] = OPTIONS,
    question: str = QUESTION,
) -> wyat.Request:
    """Construit une requête `Request.choice` fermée."""
    return wyat.Request.choice(question, dict(options), context=message)


def decider(
    modele: Decideur,
    message: str,
    options: Mapping[str, str] = OPTIONS,
    question: str = QUESTION,
) -> wyat.Decision:
    return modele.decide(requete(message, options, question))


def probas(decision: wyat.Decision) -> pd.Series:
    """Probabilités par option, triées de la plus forte à la plus faible."""
    return pd.Series(decision.probabilities_by_id).sort_values(ascending=False).round(3)


class _AvecBarre:
    """Enveloppe affichant une barre de progression pendant un lot de décisions."""

    def __init__(self, modele: Decideur, total: int) -> None:
        from tqdm.auto import tqdm

        self._modele = modele
        self.model_id = modele.model_id
        self._barre = tqdm(total=total, desc="décisions", leave=False)

    def decide(self, requete_: wyat.Request, temperature: float | None = None) -> wyat.Decision:
        decision = self._modele.decide(requete_, temperature=temperature)
        self._barre.update(1)
        if self._barre.n >= self._barre.total:
            self._barre.close()
        return decision


def preparer_lot(
    modele: Decideur,
    requetes: Sequence[wyat.Request],
    quoi: str = "décisions",
) -> tuple[Decideur, int]:
    """Annonce la durée estimée et renvoie `(decideur, nombre_a_calculer)`."""
    a_calculer = (
        sum(not modele.en_cache(r) for r in requetes)
        if isinstance(modele, ModeleAtelier)
        else len(requetes)
    )
    if 0 < a_calculer < len(requetes):
        print(f"{len(requetes) - a_calculer} décisions déjà en cache, {a_calculer} à calculer.")
    if a_calculer >= 10:
        estimation = duree_estimee(modele, a_calculer)
        if estimation:
            print(f"Durée estimée : {estimation} pour {a_calculer} {quoi}.")
        return _AvecBarre(modele, len(requetes)), a_calculer
    return modele, a_calculer


def decider_lot(
    modele: Decideur,
    requetes: Iterable[wyat.Request],
    quoi: str = "décisions",
) -> list[wyat.Decision]:
    """Exécute une séquence de requêtes avec barre de progression si nécessaire."""
    liste_requetes = list(requetes)
    cible, a_calculer = preparer_lot(modele, liste_requetes, quoi)
    debut = time.perf_counter()
    sortie = [cible.decide(r) for r in liste_requetes]
    if a_calculer:
        print(f"{len(liste_requetes)} {quoi} en {time.perf_counter() - debut:.1f} s")
    return sortie
