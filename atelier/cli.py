# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Commande `atelier` : piloter l'atelier depuis le terminal.

Exemples ::

    atelier info --vitesse
    atelier decider "on m'a prélevé deux fois" --options travail/options.toml
    atelier evaluer --options travail/options.toml --jeu dev --erreurs
    atelier seuils --jeu dev
    atelier accord travail/annotations.csv
    atelier securite commande "rm -rf node_modules" --tache "réinstaller"
    atelier securite message "Colissimo : frais de 1,99 €…" --expediteur "+33 7 56 12 84 90"
    atelier preparer && atelier verifier 4
"""
from __future__ import annotations

import argparse
from importlib.metadata import version
import json
import os
from pathlib import Path
import sys
import tomllib
import types

import pandas as pd

import atelier as at
from . import config
from .missions import FICHIERS, TITRES, TestDejaOuvert, preparer, verifier
from .options import OPTIONS, QUESTION, lire_options


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="atelier",
        description="Atelier « Modèles de décision avec wyat » : 100 % local.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--rapide", action="store_true", help="force le mode rapide (jeux dev/test réduits)")
    p.add_argument("--complet", action="store_true", help="force les jeux complets")
    p.add_argument(
        "--secours",
        action="store_true",
        help="rejoue les décisions pré-calculées, sans charger le modèle",
    )
    sous = p.add_subparsers(dest="commande", required=True, metavar="COMMANDE")

    s = sous.add_parser("info", help="environnement, moteur, mode, cache ; --vitesse mesure la vitesse")
    s.add_argument("--vitesse", action="store_true", help="charge le modèle et mesure le temps par message")

    s = sous.add_parser("decider", help="une décision sur un message")
    s.add_argument("message")
    s.add_argument("--options", help="fichier TOML d'options (défaut : options de référence)")
    s.add_argument("--json", action="store_true", help="sortie JSON (pour vos scripts)")

    s = sous.add_parser("evaluer", help="exactitude + intervalle de confiance sur un jeu étiqueté")
    s.add_argument("--options", help="fichier TOML d'options")
    s.add_argument("--jeu", default="dev", choices=["dev", "test"], help="dev (défaut) ; test = animateur seulement")
    s.add_argument("--acceptable", action="store_true", help="compte aussi les étiquettes « acceptables »")
    s.add_argument("--erreurs", action="store_true", help="affiche les erreurs")
    s.add_argument("--csv", help="écrit les résultats ligne par ligne dans ce fichier")

    s = sous.add_parser("seuils", help="table automatisation / erreurs pour chaque seuil de marge")
    s.add_argument("--options", help="fichier TOML d'options")
    s.add_argument("--jeu", default="dev", choices=["dev", "test"])
    s.add_argument("--pas", type=float, default=0.05)

    s = sous.add_parser("accord", help="accord entre annotateurs (accord brut, κ de Cohen et de Fleiss)")
    s.add_argument("fichier", nargs="?", help="CSV : numero, A1, A2… (défaut : annotations simulées)")

    s = sous.add_parser("securite", help="bloc 6 : garde-fou de commandes, arnaques, injection")
    ss = s.add_subparsers(dest="quoi", required=True, metavar="QUOI")
    c = ss.add_parser("commande", help="une commande proposée par un agent IA")
    c.add_argument("cmd", metavar="COMMANDE_SHELL")
    c.add_argument("--tache", default="", help="ce que l'utilisateur a demandé à l'agent")
    c.add_argument("--config", help="fichier TOML avec une section [garde]")
    c = ss.add_parser("message", help="un SMS ou e-mail reçu")
    c.add_argument("message")
    c.add_argument("--expediteur", default="")
    c.add_argument("--canal", default="SMS")
    c.add_argument("--signaux", action="store_true", help="ajoute les questions oui / non explicatives")
    c = ss.add_parser("injection", help="P(injection de prompt) d'un texte (limite : rate les cas subtils)")
    c.add_argument("texte")
    c = ss.add_parser("evaluer", help="évalue garde et arnaques sur dev")
    c.add_argument("--config", help="fichier TOML [garde] / [arnaques]")
    c.add_argument("--jeu", default="dev", choices=["dev", "test"])

    sous.add_parser("missions", help="liste des missions et de leurs fichiers")
    s = sous.add_parser("preparer", help="copie les fichiers de départ des missions dans travail/")
    s.add_argument("--dossier", default=None)
    s = sous.add_parser("verifier", help="vérifie une mission sur dev (--final : test scellé, animateur)")
    s.add_argument("mission", type=int, choices=range(1, 7))
    s.add_argument("--dossier", default=None, help="dossier de travail (défaut : travail/)")
    s.add_argument(
        "--final",
        action="store_true",
        help="ouvre le test scellé, une seule fois (ATELIER_ANIMATEUR=1 requis)",
    )
    s.add_argument(
        "--encore",
        action="store_true",
        help="rouvre un test scellé déjà ouvert (marqué « plus scellé »)",
    )
    return p


def _compter_lignes(chemin: Path) -> int:
    if not chemin.exists():
        return 0
    with chemin.open(encoding="utf-8") as fichier:
        return sum(1 for _ in fichier)


def _refuser_test(jeu: str) -> None:
    if jeu == "test" and not config.animateur():
        sys.exit("Le test scellé ne s'ouvre qu'une fois, par l'animateur : ATELIER_ANIMATEUR=1 atelier … --jeu test")


def _options(chemin: str | None) -> tuple[dict[str, str], str]:
    if not chemin:
        return OPTIONS, QUESTION
    contrat = lire_options(chemin)
    return contrat.options, contrat.question


def _cmd_info(args: argparse.Namespace) -> int:
    print(f"atelier {at.__version__} · wyat {version('wyat')} · racine {config.RACINE}")
    mode_txt = "rapide" if config.mode_rapide() else "complet"
    secours_txt = "oui" if config.precalcule_seul() else "non"
    print(
        f"modèle {config.modele()} · backend {config.backend()} · device {config.device()} · "
        f"mode {mode_txt} · secours {secours_txt}"
    )
    n_cache = _compter_lignes(config.CACHE_LOCAL)
    n_pre = _compter_lignes(config.PRECALCULE)
    print(f"cache local : {n_cache} décisions · pré-calculé : {n_pre} décisions")
    print(f"dev : {len(at.lire('dev', verbeux=False))} messages · test : {len(at.lire('test', verbeux=False))} messages")
    if args.vitesse:
        at.charger_modele()
    return 0


def _cmd_accord(args: argparse.Namespace) -> int:
    fichier = args.fichier or config.DATASET / "annotations_exemple_SIMULEES.csv"
    table = pd.read_csv(fichier, dtype=str).fillna("")
    cols = [c for c in table.columns if c.startswith("A") and (table[c] != "").all()]
    kappa, _ = at.kappa_fleiss(table[cols])
    print(f"{fichier} : {len(cols)} annotateurs, {len(table)} messages")
    k_cohen = at.kappa_cohen(table[cols[0]], table[cols[1]])
    print(
        f"accord brut moyen {100 * at.accord_moyen(table[cols]):.1f} % · "
        f"κ Cohen({cols[0]}, {cols[1]}) {k_cohen:.3f} · "
        f"κ Fleiss {kappa:.3f} ({at.interpretation_kappa(kappa)})"
    )
    return 0


def _cmd_missions() -> int:
    for n, titre in TITRES.items():
        print(f"{n}. {titre:<42} fichier : travail/{FICHIERS[n]}")
    print("Énoncés : missions/*/MISSION.md · vérifier : atelier verifier N")
    return 0


def _cmd_preparer(dossier: Path) -> int:
    copies = preparer(dossier)
    if copies:
        print("\n".join(f"créé : {c}" for c in copies))
    else:
        print(f"rien à copier : {dossier} contient déjà les fichiers")
    return 0


def _cmd_verifier(args: argparse.Namespace, dossier: Path) -> int:
    if args.final and not config.animateur():
        sys.exit("--final ouvre le test scellé : réservé à l'animateur (ATELIER_ANIMATEUR=1).")
    modele = None if args.mission in (2, 3) else at.charger_modele(verbeux=False)
    try:
        res = verifier(args.mission, modele, dossier, final=args.final, encore=args.encore)
    except TestDejaOuvert as erreur:
        sys.exit(str(erreur))
    print(res.texte())
    return 0 if res.reussi else 1


def _cmd_decider(args: argparse.Namespace, modele: at.ModeleAtelier) -> int:
    options, question = _options(args.options)
    decision = at.decider(modele, args.message, options, question)
    if args.json:
        payload = {
            **decision.to_dict(),
            "marge": decision.probability_margin,
            "probabilites": decision.probabilities_by_id,
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 0
    print(f"choix : {decision.selected}   marge : {decision.probability_margin:.3f}")
    print(at.probas(decision).to_string())
    return 0


def _cmd_evaluer_ou_seuils(args: argparse.Namespace, modele: at.ModeleAtelier) -> int:
    _refuser_test(args.jeu)
    options, question = _options(args.options)
    jeu = at.lire(args.jeu, verbeux=True)
    strict = not getattr(args, "acceptable", False)
    rapport, res = at.evaluer(modele, jeu, options, strict=strict, question=question)
    if args.commande == "seuils":
        seuils = [round(args.pas * i, 2) for i in range(int(1 / args.pas))]
        print(at.courbe_selective(rapport, seuils).to_string(index=False))
        return 0

    acc, bas, haut = at.intervalle_bootstrap(res.correct)
    ece_val = rapport.expected_calibration_error or 0.0
    print(f"exactitude {acc:.1%}  IC 95 % [{bas:.1%} ; {haut:.1%}]  n = {len(res)}  ·  ECE {ece_val:.3f}")
    print(res.groupby("label").correct.agg(["mean", "count"]).round(2).to_string())
    if args.erreurs:
        print(res[~res.correct][["message", "label", "prediction", "marge"]].to_string(index=False))
    if args.csv:
        res.to_csv(args.csv, index=False)
        print(f"écrit : {args.csv}")
    return 0


def _cmd_securite(args: argparse.Namespace, modele: at.ModeleAtelier) -> int:
    if args.quoi == "commande":
        reglage = at.ReglageGarde.depuis_toml(args.config) if args.config else at.ReglageGarde()
        action, raison, _ = at.garde(modele, args.tache, args.cmd, reglage=reglage)
        print(f"{action.upper()}  ({raison})")
        return 0

    if args.quoi == "message":
        proba = at.p_arnaque(modele, args.canal, args.expediteur, args.message)
        print(f"P(frauduleux) = {proba:.2f}")
        if args.signaux:
            entree = types.SimpleNamespace(canal=args.canal, expediteur=args.expediteur, message=args.message)
            for cle, val in at.signaux_arnaque(modele, entree).items():
                print(f"  {cle:<13} P(oui) = {val:.2f}")
        return 0

    if args.quoi == "injection":
        proba_inj = at.p_injection(modele, args.texte)
        print(f"P(injection) = {proba_inj:.2f}   (attention : rate souvent les injections subtiles)")
        return 0

    if args.quoi == "evaluer":
        _refuser_test(args.jeu)
        reglage = at.ReglageGarde.depuis_toml(args.config) if args.config else at.ReglageGarde()
        seuil_arnaque = (
            float(tomllib.loads(Path(args.config).read_text(encoding="utf-8")).get("arnaques", {}).get("seuil", 0.4))
            if args.config
            else 0.4
        )
        suffixe = "test_scelle" if args.jeu == "test" else "dev"
        res_garde = at.evaluer_garde(modele, at.lire_secu(f"commandes_{suffixe}.csv"), reglage=reglage)
        print(pd.Series(at.bilan_garde(res_garde)).to_string())
        res_arnaques = at.evaluer_arnaques(modele, at.lire_secu(f"messages_{suffixe}.csv"))
        print(pd.Series(at.bilan_arnaques(res_arnaques, seuil_arnaque)).to_string())
        return 0

    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.rapide:
        os.environ["WYAT_MODE"] = "rapide"
    if args.complet:
        os.environ["WYAT_MODE"] = "complet"
    if args.secours:
        os.environ["WYAT_PRECALCULE"] = "1"

    pd.set_option("display.width", 160)
    pd.set_option("display.max_colwidth", 70)
    dossier = Path(getattr(args, "dossier", None) or config.RACINE / "travail")

    try:
        if args.commande == "info":
            return _cmd_info(args)
        if args.commande == "accord":
            return _cmd_accord(args)
        if args.commande == "missions":
            return _cmd_missions()
        if args.commande == "preparer":
            return _cmd_preparer(dossier)
        if args.commande == "verifier":
            return _cmd_verifier(args, dossier)

        modele = at.charger_modele(verbeux=False)
        if args.commande == "decider":
            return _cmd_decider(args, modele)
        if args.commande in ("evaluer", "seuils"):
            return _cmd_evaluer_ou_seuils(args, modele)
        if args.commande == "securite":
            return _cmd_securite(args, modele)
    except (ValueError, at.DecisionNonPrecalculee) as erreur:
        print(f"Erreur : {erreur}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
