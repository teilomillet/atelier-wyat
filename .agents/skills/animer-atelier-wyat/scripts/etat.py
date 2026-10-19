#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Où en est la séance ? Lecture seule, sans modèle, bibliothèque standard uniquement.

Usage (depuis la racine du dépôt) : python3 .agents/skills/animer-atelier-wyat/scripts/etat.py [--dossier travail]
"""
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[4]
JOURNAL_SCELLE = ".scelle_ouvert.jsonl"   # écrit par atelier.missions.verifier(final=True)


def _contenu(chemin: Path) -> list[str]:
    """Le contenu sans les lignes d'en-tête SPDX : un changement de licence n'est pas du travail."""
    return [l for l in chemin.read_text(encoding="utf-8").splitlines() if "SPDX-" not in l]


def main() -> None:
    dossier = RACINE / (sys.argv[sys.argv.index("--dossier") + 1] if "--dossier" in sys.argv else "travail")
    modele = Path.home() / ".cache" / "wyat" / "wyat-1-800m"
    print("Environnement")
    print(f"  .venv/bin/atelier : {'présent' if (RACINE / '.venv/bin/atelier').exists() else 'ABSENT → demander avant ./scripts/installer.sh'}")
    print(f"  modèle ({modele}) : {'présent' if modele.exists() else 'absent (ou WYAT_MODEL ailleurs) → sinon : atelier --secours …'}")

    print(f"\nTravail ({dossier.relative_to(RACINE) if dossier.is_relative_to(RACINE) else dossier})")
    if not dossier.exists():
        print("  absent → .venv/bin/atelier preparer")
    else:
        # Mêmes fichiers que `atelier preparer` : missions/<étape>/depart_X → travail/X
        for depart in sorted((RACINE / "missions").glob("*/depart_*")):
            cible = dossier / depart.name.removeprefix("depart_")
            if not cible.exists():
                etat = "absent"
            elif _contenu(depart) == _contenu(cible):
                etat = "non commencé (identique au départ)"
            else:
                etat = "modifié"
            print(f"  étape {depart.parent.name:<26} {cible.name:<18} {etat}")
        for extra in ("garde.py", "mon_cas.toml"):
            if (dossier / extra).exists():
                print(f"  {'':<33} {extra:<18} présent")

    print("\nTest scellé")
    journal = dossier / JOURNAL_SCELLE
    ouvertures = [json.loads(l) for l in journal.read_text(encoding="utf-8").splitlines() if l.strip()] if journal.exists() else []
    if not ouvertures:
        print("  jamais ouvert : options et seuils peuvent encore changer")
    for o in ouvertures:
        print(f"  étape {o['mission']} ouverte le {o['date']} : {'réussie' if o['reussi'] else 'échouée'} (figé : plus de réglage)")

    print("\nJournal de l'animateur (dernières lignes)")
    notes = dossier / "journal_animateur.md"
    if notes.exists():
        for ligne in [l for l in notes.read_text(encoding="utf-8").splitlines() if l.strip()][-8:]:
            print(f"  {ligne}")
    else:
        print("  absent → nouvelle séance (AGENTS.md §1), le créer")


if __name__ == "__main__":
    main()
