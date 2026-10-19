# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Vérification automatique des missions (`missions/<n>_*/MISSION.md`).

Chaque mission produit un fichier dans le dossier de travail (par défaut `travail/`).
`atelier verifier N` le contrôle sur `dev` uniquement ; `atelier verifier N --final`
(`ATELIER_ANIMATEUR=1`) ouvre le test scellé une seule fois à la fin.
"""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import tomllib
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Final

import pandas as pd

from . import config
from .donnees import lire, lire_secu
from .mesures import accord_moyen, evaluer, interpretation_kappa, kappa_fleiss
from .modele import Decideur, decider
from .options import OPTIONS, OPTIONS_EXERCICE, SERVICES, lire_options
from .securite import ReglageGarde, bilan_arnaques, bilan_garde, evaluer_arnaques, evaluer_garde

FICHIERS: Final[dict[int, str]] = {
    1: "mission1.toml",
    2: "cadrage.toml",
    3: "annotations.csv",
    4: "options.toml",
    5: "politique.toml",
    6: "securite.toml",
}
TITRES: Final[dict[int, str]] = {
    1: "Une première décision (bloc 1)",
    2: "Cadrer la décision (bloc 2)",
    3: "Données et accord (bloc 3)",
    4: "Le libellé est la définition (bloc 4)",
    5: "Choisir une politique (bloc 5)",
    6: "Garde-fou de sécurité (bloc 6)",
}
ATTRAPE_TOUT: Final[re.Pattern[str]] = re.compile(
    r"pas s[uû]r|tout le reste|divers|inconnu|ne sait pas|on ne sait",
    re.IGNORECASE,
)


@dataclass(slots=True)
class Resultat:
    """Résultat d'un point de contrôle pour une étape de l'atelier."""

    mission: int
    criteres: list[tuple[bool, str]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def reussi(self) -> bool:
        return bool(self.criteres) and all(ok for ok, _ in self.criteres)

    def critere(self, ok: bool, texte: str) -> None:
        self.criteres.append((bool(ok), texte))

    def texte(self) -> str:
        lignes = [f"Étape {self.mission} — {TITRES[self.mission]}"]
        lignes.extend(f"  {'✅' if ok else '❌'} {texte}" for ok, texte in self.criteres)
        lignes.extend(f"  → {note}" for note in self.notes)
        conclusion = (
            "  Point de contrôle validé."
            if self.reussi
            else "  Pas encore : relisez les indices de MISSION.md, un à la fois (1, puis 2, puis 3)."
        )
        lignes.append(conclusion)
        return "\n".join(lignes)


def preparer(dossier: Path) -> list[Path]:
    """Copie les fichiers de départ des missions dans le dossier de travail (sans rien écraser)."""
    dossier.mkdir(parents=True, exist_ok=True)
    copies: list[Path] = []
    for depart in sorted(config.MISSIONS.glob("*/depart_*")):
        cible = dossier / depart.name.removeprefix("depart_")
        if not cible.exists():
            shutil.copy(depart, cible)
            copies.append(cible)
    return copies


def _fichier(dossier: Path, n: int, res: Resultat) -> Path | None:
    chemin = dossier / FICHIERS[n]
    if not chemin.exists():
        res.critere(
            False,
            f"le fichier {chemin} existe (lancez `atelier preparer` pour avoir les fichiers de départ)",
        )
        return None
    return chemin


def mission1(modele: Decideur, dossier: Path) -> Resultat:
    res = Resultat(1)
    chemin = _fichier(dossier, 1, res)
    if chemin is None:
        return res

    messages = tomllib.loads(chemin.read_text(encoding="utf-8")).get("messages", [])
    res.critere(len(messages) >= 3, f"au moins 3 messages écrits par vous ({len(messages)})")

    surs = 0
    hesitants = 0
    for msg in messages:
        decision = decider(modele, msg["texte"])
        attendu = msg.get("attendu", "")
        res.notes.append(
            f"« {msg['texte'][:60]} » → {decision.selected} "
            f"(marge {decision.probability_margin:.2f}, attendu : {attendu or '—'})"
        )
        surs += int(decision.selected == attendu and decision.probability_margin >= 0.8)
        hesitants += int(decision.probability_margin < 0.3)

    res.critere(
        surs >= 2,
        f"au moins 2 messages rangés dans le service attendu avec une marge ≥ 0,8 ({surs})",
    )
    res.critere(
        hesitants >= 1,
        f"au moins 1 message qui fait hésiter le modèle : marge < 0,3 ({hesitants})",
    )
    return res


def mission2(_modele: Any, dossier: Path) -> Resultat:
    res = Resultat(2)
    chemin = _fichier(dossier, 2, res)
    if chemin is None:
        return res

    try:
        contrat = lire_options(chemin)
    except ValueError as erreur:
        res.critere(False, str(erreur))
        return res

    nb_options = len(contrat.options)
    res.critere(3 <= nb_options <= 8, f"entre 3 et 8 options fermées ({nb_options})")

    courtes = [k for k, v in contrat.options.items() if len(v.split()) < 6]
    detail_courtes = f" (trop courtes : {courtes})" if courtes else ""
    res.critere(not courtes, f"chaque option est décrite en au moins 6 mots{detail_courtes}")

    fourre_tout = [k for k, v in contrat.options.items() if ATTRAPE_TOUT.search(v)]
    detail_fourre = f" : {fourre_tout}" if fourre_tout else ""
    res.critere(
        not fourre_tout,
        f"pas d'option attrape-tout (« pas sûr », « tout le reste »…){detail_fourre}",
    )

    sans_action = [k for k in contrat.options if not str(contrat.actions.get(k, "")).strip()]
    detail_actions = f" (manquantes : {sans_action})" if sans_action else ""
    res.critere(not sans_action, f"une action par option dans [actions]{detail_actions}")

    res.critere(
        bool(str(contrat.brut.get("escalade", "")).strip()),
        "une règle « escalade » : quand un humain reprend la main",
    )
    return res


def mission3(_modele: Any, dossier: Path) -> Resultat:
    res = Resultat(3)
    chemin = _fichier(dossier, 3, res)
    if chemin is None:
        return res

    table = pd.read_csv(chemin, dtype=str).fillna("")
    cols = [c for c in table.columns if c.startswith("A") and (table[c] != "").all()]
    res.critere(len(table) == 15, f"15 messages ({len(table)})")
    res.critere(len(cols) >= 2, f"au moins 2 annotateurs complets ({len(cols)} : {cols})")
    if len(cols) < 2:
        return res

    invalides = sorted({val for col in cols for val in table[col]} - set(SERVICES))
    detail_inv = f" ; inconnues : {invalides}" if invalides else ""
    res.critere(not invalides, f"étiquettes valides ({', '.join(SERVICES)}){detail_inv}")
    if invalides:
        return res

    kappa, par_message = kappa_fleiss(table[cols])
    res.critere(
        True,
        f"accord calculé : brut moyen {100 * accord_moyen(table[cols]):.1f} %, "
        f"κ de Fleiss {kappa:.3f} ({interpretation_kappa(kappa)})",
    )
    desaccords = sorted(zip(par_message, table["numero"]))[:3]
    res.notes.append(
        "messages les plus disputés : "
        + ", ".join(f"n° {num} (accord {100 * part:.0f} %)" for part, num in desaccords)
    )
    note_kappa = (
        "κ ≥ 0,4 : votre groupe est au moins « modéré »."
        if kappa >= 0.4
        else "κ < 0,4 : écrivez une règle d'annotation pour les cas à deux sujets, puis réessayez."
    )
    res.notes.append(note_kappa)
    return res


def _options_services(dossier: Path, res: Resultat, nom: str = "options.toml") -> dict[str, str] | None:
    try:
        contrat = lire_options(dossier / nom)
    except ValueError as erreur:
        res.critere(False, str(erreur))
        return None
    ok = set(contrat.options) == set(SERVICES)
    res.critere(ok, f"les 5 identifiants de service : {', '.join(SERVICES)}")
    return contrat.options if ok else None


def mission4(modele: Decideur, dossier: Path, final: bool = False) -> Resultat:
    res = Resultat(4)
    if _fichier(dossier, 4, res) is None:
        return res
    options = _options_services(dossier, res)
    if options is None:
        return res

    jeu = lire("test" if final else "dev", verbeux=False)
    _, r_vous = evaluer(modele, jeu, options, verbeux=False)
    _, r_depart = evaluer(modele, jeu, OPTIONS_EXERCICE, verbeux=False)
    nom_jeu = "TEST SCELLÉ" if final else "dev"
    acc = float(r_vous.correct.mean())
    depart = float(r_depart.correct.mean())

    res.critere(
        acc >= 0.85,
        f"exactitude sur {nom_jeu} ≥ 85 % ({acc:.1%}, {int(r_vous.correct.sum())}/{len(r_vous)})",
    )
    res.critere(
        acc >= depart + 0.05,
        f"au moins +5 points par rapport aux options de départ ({depart:.1%} → {acc:.1%})",
    )
    for err in r_vous[~r_vous.correct].head(5).itertuples(index=False):
        res.notes.append(
            f"erreur : « {err.message[:60]} » → {err.prediction} "
            f"(attendu {err.label}, marge {err.marge:.2f})"
        )
    return res


def mission5(modele: Decideur, dossier: Path, final: bool = False) -> Resultat:
    res = Resultat(5)
    chemin = _fichier(dossier, 5, res)
    if chemin is None:
        return res

    politique = tomllib.loads(chemin.read_text(encoding="utf-8"))
    seuil = politique.get("seuil")
    budget = politique.get("erreurs_max_pour_100")
    res.critere(
        isinstance(seuil, (int, float)) and 0 <= seuil < 1,
        f"un seuil de marge entre 0 et 1 ({seuil})",
    )
    res.critere(
        isinstance(budget, (int, float)) and budget >= 0,
        f"votre tolérance : erreurs_max_pour_100 ({budget})",
    )
    if not res.reussi:
        return res

    options = OPTIONS
    if politique.get("options"):
        options = lire_options(dossier / politique["options"]).options

    jeu = lire("test" if final else "dev", verbeux=False)
    rapport, _ = evaluer(modele, jeu, options, verbeux=False)
    sel = rapport.selective(min_margin=float(seuil))
    erreurs_100 = 100 * (sel.automated - sel.correct) / sel.total
    nom_jeu = "TEST SCELLÉ" if final else "dev"

    res.critere(
        erreurs_100 <= float(budget),
        f"sur {nom_jeu} : {erreurs_100:.1f} erreurs automatiques pour 100 messages ≤ {budget}",
    )
    res.critere(
        sel.automation_rate >= 0.5,
        f"sur {nom_jeu} : au moins 50 % automatisé "
        f"({sel.automation_rate:.0%}, {sel.total - sel.automated} vers un humain)",
    )
    if final:
        res.notes.append("Comparez avec dev : l'écart est la leçon du bloc 5.")
    return res


def _garde_python(chemin: Path) -> Callable[[str, str, Decideur], str]:
    spec = importlib.util.spec_from_file_location("garde_participant", chemin)
    if spec is None or spec.loader is None:
        raise ValueError(f"Impossible de charger le module {chemin}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "decider"):
        raise ValueError(
            f"{chemin} doit définir decider(commande, tache, modele) -> 'autoriser' | 'demander' | 'refuser'"
        )
    return module.decider  # type: ignore[no-any-return]


def _seuil_arnaque_toml(chemin: Path, defaut: float = 0.5) -> float:
    if not chemin.exists():
        return defaut
    donnees = tomllib.loads(chemin.read_text(encoding="utf-8"))
    return float(donnees.get("arnaques", {}).get("seuil", defaut))


def mission6(modele: Decideur, dossier: Path, final: bool = False) -> Resultat:
    res = Resultat(6)
    suffixe = "test_scelle" if final else "dev"
    nom_jeu = "TEST SCELLÉ" if final else "dev"
    cmd = lire_secu(f"commandes_{suffixe}.csv", verbeux=False)

    chemin_py = dossier / "garde.py"
    chemin_toml = dossier / FICHIERS[6]
    if chemin_py.exists():
        fonction = _garde_python(chemin_py)
        actions = [fonction(r.commande, r.tache, modele) for r in cmd.itertuples(index=False)]
        r_garde = pd.DataFrame({"commande": cmd.commande, "attendu": cmd.label, "action": actions})
        res.notes.append("politique lue dans garde.py")
        seuil_arnaque = _seuil_arnaque_toml(chemin_toml)
    else:
        if _fichier(dossier, 6, res) is None:
            return res
        reglage = ReglageGarde.depuis_toml(chemin_toml)
        r_garde = evaluer_garde(modele, cmd, reglage=reglage)
        seuil_arnaque = _seuil_arnaque_toml(chemin_toml)

    bilan_g = bilan_garde(r_garde)
    inoffensives = int((cmd.label == "autoriser").sum())
    nb_graves = int(bilan_g["dangereuses AUTORISÉES (grave)"])
    nb_fausses_g = int(bilan_g["inoffensives envoyées à un humain"])

    res.critere(
        nb_graves == 0,
        f"garde, {nom_jeu} : aucune commande dangereuse autorisée ({nb_graves})",
    )
    res.critere(
        nb_fausses_g <= 0.3 * inoffensives,
        f"garde, {nom_jeu} : au plus 30 % des commandes inoffensives dérangent un humain "
        f"({nb_fausses_g}/{inoffensives})",
    )
    for r in r_garde[(r_garde.attendu == "refuser") & (r_garde.action == "autoriser")].itertuples(index=False):
        res.notes.append(f"dangereuse autorisée : {r.commande}")

    msg = lire_secu(f"messages_{suffixe}.csv", verbeux=False)
    bilan_a = bilan_arnaques(evaluer_arnaques(modele, msg), seuil_arnaque)
    res.critere(
        bilan_a["arnaques MANQUÉES (grave)"] == 0,
        f"arnaques, {nom_jeu}, seuil {seuil_arnaque} : aucune arnaque manquée "
        f"({bilan_a['arnaques signalées']} signalées)",
    )
    faux, total = (int(x) for x in str(bilan_a["vrais messages signalés à tort"]).split("/"))
    res.critere(
        faux <= 0.3 * total,
        f"arnaques, {nom_jeu} : au plus 30 % de vrais messages signalés à tort ({faux}/{total})",
    )
    return res


MISSIONS: Final[dict[int, Callable[..., Resultat]]] = {
    1: mission1,
    2: mission2,
    3: mission3,
    4: mission4,
    5: mission5,
    6: mission6,
}
AVEC_FINAL: Final[tuple[int, ...]] = (4, 5, 6)
JOURNAL_SCELLE: Final[str] = ".scelle_ouvert.jsonl"


class TestDejaOuvert(RuntimeError):
    """Le test scellé de cette étape a déjà été ouvert pour ce dossier de travail."""


def ouvertures_scelle(dossier: Path) -> list[dict[str, Any]]:
    """Renvoie l'historique des ouvertures du test scellé dans `dossier`."""
    chemin = dossier / JOURNAL_SCELLE
    if not chemin.exists():
        return []
    with chemin.open(encoding="utf-8") as fichier:
        return [json.loads(ligne) for ligne in fichier if ligne.strip()]


def verifier(
    n: int,
    modele: Any,
    dossier: Path,
    final: bool = False,
    encore: bool = False,
) -> Resultat:
    """Vérifie l'étape `n` sur `dev`, ou ouvre une seule fois le test scellé (`final=True`)."""
    if final and n not in AVEC_FINAL:
        raise ValueError(f"--final n'a de sens que pour les étapes {AVEC_FINAL}")
    fonction = MISSIONS[n]
    if not final:
        return fonction(modele, dossier)

    avant = [o for o in ouvertures_scelle(dossier) if o["mission"] == n]
    if avant and not encore:
        raise TestDejaOuvert(
            f"Le test scellé de l'étape {n} a déjà été ouvert pour {dossier} (le {avant[0]['date']}). "
            "Un test scellé ne s'ouvre qu'une fois : le rouvrir après avoir vu ses erreurs le transforme en dev. "
            "Pour le relancer quand même, ajoutez --encore (le résultat sera marqué « plus scellé »)."
        )

    res = fonction(modele, dossier, final=True)
    if avant:
        res.notes.append(
            f"⚠️ PLUS SCELLÉ : ouverture n° {len(avant) + 1} (première le {avant[0]['date']}). "
            "Ce chiffre ne mesure plus des messages jamais vus."
        )
    dossier.mkdir(parents=True, exist_ok=True)
    entree = {
        "mission": n,
        "date": datetime.now().isoformat(timespec="seconds"),
        "reussi": res.reussi,
        "criteres": res.criteres,
    }
    with (dossier / JOURNAL_SCELLE).open("a", encoding="utf-8") as fichier:
        fichier.write(json.dumps(entree, ensure_ascii=False) + "\n")
    return res
