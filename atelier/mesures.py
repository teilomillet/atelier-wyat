# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Mesures : évaluation, intervalle bootstrap, calibration, politique à seuil et accord entre annotateurs."""
from __future__ import annotations

import itertools
import random
import time
from collections import Counter
from collections.abc import Mapping, Sequence

import pandas as pd
import wyat
from wyat.evaluation import EvaluationCase, EvaluationReport, evaluate

from .modele import Decideur, decider, preparer_lot, requete
from .options import OPTIONS, QUESTION


def evaluer(
    modele: Decideur,
    df: pd.DataFrame,
    options: Mapping[str, str] = OPTIONS,
    strict: bool = True,
    question: str = QUESTION,
    verbeux: bool = True,
) -> tuple[EvaluationReport, pd.DataFrame]:
    """Évalue un jeu de données (colonnes `id`, `message`, `label`, `labels_acceptables`, `difficulte`).

    Args:
        modele: Modèle `wyat` ou `ModeleAtelier`.
        df: Tableau de messages à évaluer.
        options: Dictionnaire d'options fermées `{identifiant: description}`.
        strict: Si `True`, seule l'étiquette principale `label` est comptée juste.
        question: Question posée au modèle.
        verbeux: Affiche le temps d'évaluation.

    Returns:
        Un tuple `(EvaluationReport, DataFrame détaillé ligne par ligne)`.
    """
    cas: list[EvaluationCase] = []
    for ligne_df in df.itertuples(index=False):
        attendu = (ligne_df.label,) if strict else tuple(str(ligne_df.labels_acceptables).split("|"))
        cas.append(
            EvaluationCase(
                id=ligne_df.id,
                request=requete(ligne_df.message, options, question),
                expected=attendu,
            )
        )

    cible, a_calculer = (
        preparer_lot(modele, [c.request for c in cas], "messages")
        if verbeux
        else (modele, len(cas))
    )
    debut = time.perf_counter()
    rapport = evaluate(cible, cas)
    duree = time.perf_counter() - debut

    lignes = []
    for r, row in zip(df.itertuples(index=False), rapport.rows):
        decision = row.prediction
        probas_id = decision.probabilities_by_id
        lignes.append({
            "id": r.id,
            "message": r.message,
            "label": r.label,
            "prediction": decision.selected,
            "correct": row.correct,
            "acceptable": decision.selected in str(r.labels_acceptables).split("|"),
            "proba_max": round(max(probas_id.values()), 3),
            "marge": round(decision.probability_margin, 3),
            "2e_choix": decision.ranking[1],
            "difficulte": r.difficulte,
        })

    if verbeux and len(df) > 0:
        ms_par_msg = 1000 * duree / len(df)
        suffixe = ", cache compris)" if a_calculer < len(cas) else ")"
        print(f"{len(df)} messages évalués en {duree:.1f} s ({ms_par_msg:.0f} ms/message{suffixe}")
    return rapport, pd.DataFrame(lignes)


def intervalle_bootstrap(
    corrects: Sequence[bool],
    n: int = 2000,
    graine: int = 17,
    niveau: float = 0.95,
) -> tuple[float, float, float]:
    """Renvoie `(exactitude, borne_basse, borne_haute)` par bootstrap percentile reproductible."""
    valeurs = [bool(x) for x in corrects]
    k = len(valeurs)
    if k == 0:
        return 0.0, 0.0, 0.0
    rng = random.Random(graine)
    stats = sorted(sum(rng.choice(valeurs) for _ in range(k)) / k for _ in range(n))
    idx_bas = int((1 - niveau) / 2 * n)
    idx_haut = int((1 + niveau) / 2 * n) - 1
    return sum(valeurs) / k, stats[idx_bas], stats[idx_haut]


def table_fiabilite(
    res: pd.DataFrame,
    bornes: Sequence[float] = (0.0, 0.5, 0.7, 0.9, 1.0),
) -> pd.DataFrame:
    """Diagramme de fiabilité en tableau : probabilité annoncée moyenne vs part correcte par tranche."""
    tranches = pd.cut(res.proba_max, list(bornes))
    return (
        res.groupby(tranches, observed=True)
        .agg(proba_annoncee=("proba_max", "mean"), exactitude=("correct", "mean"), n=("correct", "size"))
        .round(3)
    )


def ece(rapport: EvaluationReport) -> float | None:
    """Erreur de calibration attendue (ECE, `0` = parfait), calculée par `wyat`."""
    return rapport.expected_calibration_error


def courbe_selective(
    rapport: EvaluationReport,
    seuils: Sequence[float] | None = None,
) -> pd.DataFrame:
    """Pour chaque seuil de marge : part automatisée, exactitude et erreurs sur la part automatisée."""
    paliers = [round(0.05 * i, 2) for i in range(20)] if seuils is None else list(seuils)
    lignes = []
    for seuil in paliers:
        sel = rapport.selective(min_margin=seuil)
        erreurs = sel.automated - sel.correct
        lignes.append({
            "seuil_marge": seuil,
            "automatise_%": round(100 * sel.automation_rate, 1),
            "vers_humain": sel.total - sel.automated,
            "exactitude_auto_%": None if sel.accuracy is None else round(100 * sel.accuracy, 1),
            "erreurs_auto": erreurs,
            "erreurs_pour_100_messages": round(100 * erreurs / sel.total, 1),
        })
    return pd.DataFrame(lignes)


def router(
    modele: Decideur,
    message: str,
    seuil: float,
    options: Mapping[str, str] = OPTIONS,
) -> tuple[str, str]:
    """Politique de routage : renvoie `(service_ou_humain, explication)`."""
    try:
        decision = decider(modele, message, options)
    except wyat.ModelInputError as erreur:
        return "humain", f"refusé ({erreur.reason})"
    if decision.probability_margin < seuil:
        premier, second = decision.ranking[0], decision.ranking[1]
        return "humain", f"incertain (marge {decision.probability_margin:.2f}, hésite entre {premier} et {second})"
    return decision.selected, f"automatique (marge {decision.probability_margin:.2f})"


def accord(a: Sequence[str], b: Sequence[str]) -> float:
    """Proportion d'éléments où deux annotateurs ont choisi la même étiquette."""
    if len(a) == 0:
        return 0.0
    return sum(x == y for x, y in zip(a, b)) / len(a)


def accord_moyen(table: pd.DataFrame) -> float:
    """Accord brut moyen sur toutes les paires de colonnes d'annotateurs."""
    paires = [accord(table[i], table[j]) for i, j in itertools.combinations(table.columns, 2)]
    return sum(paires) / len(paires) if paires else 0.0


def kappa_cohen(a: Sequence[str], b: Sequence[str]) -> float:
    """Coefficient $\\kappa$ de Cohen entre deux annotateurs."""
    n = len(a)
    if n == 0:
        return 0.0
    po = accord(a, b)
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def kappa_fleiss(table: pd.DataFrame) -> tuple[float, list[float]]:
    """Coefficient $\\kappa$ de Fleiss multi-annotateurs ; renvoie `(kappa, accord_par_ligne)`."""
    nb_lignes, nb_annotateurs = len(table), table.shape[1]
    comptes = [Counter(row) for row in table.values]
    denom = nb_annotateurs * (nb_annotateurs - 1)
    accord_ligne = [(sum(c * c for c in cnt.values()) - nb_annotateurs) / denom for cnt in comptes]
    categories = set().union(*comptes)
    parts_cat = {k: sum(cnt[k] for cnt in comptes) / (nb_lignes * nb_annotateurs) for k in categories}
    p_bar = sum(accord_ligne) / nb_lignes
    p_hasard = sum(v * v for v in parts_cat.values())
    kappa = (p_bar - p_hasard) / (1 - p_hasard) if p_hasard < 1 else 1.0
    return kappa, accord_ligne


def interpretation_kappa(k: float) -> str:
    """Barème usuel de Landis & Koch."""
    for borne, qualificatif in ((0.2, "faible"), (0.4, "passable"), (0.6, "modéré"), (0.8, "bon")):
        if k < borne:
            return qualificatif
    return "très bon"
