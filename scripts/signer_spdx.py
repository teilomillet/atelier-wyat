# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Ajoute ou met à jour l'en-tête SPDX sur les fichiers sources versionnés (idempotent).

Les fichiers de données et binaires (CSV, JSONL, ipynb, HTML, PDF, sorties .txt) sont couverts par LICENSE et NOTICE.
Usage : python scripts/signer_spdx.py [--verifier]
"""
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
AUTEUR = "2026 Teïlo Millet - teilomillet"
LICENCE = "PolyForm-Noncommercial-1.0.0"
# Fichiers de licence eux-mêmes : couverts par LICENSE.
GENERES = {"LICENSE"}


def entete(suffixe: str) -> str | None:
    lignes = (f"SPDX-FileCopyrightText: {AUTEUR}", f"SPDX-License-Identifier: {LICENCE}")
    if suffixe in {".py", ".sh", ".toml", ".gitignore", ".cfg", ".yml", ".yaml", "NOTICE"}:
        return "".join(f"# {l}\n" for l in lignes)
    if suffixe == ".md":
        return "<!--\n" + "".join(f"{l}\n" for l in lignes) + "-->\n"
    return None


def a_signer() -> list[Path]:
    noms = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                          cwd=RACINE, capture_output=True, text=True, check=True).stdout.split()
    sortie = []
    for nom in noms:
        if nom in GENERES:
            continue
        chemin = RACINE / nom
        suffixe = chemin.suffix or chemin.name
        if chemin.is_file() and entete(suffixe):
            sortie.append(chemin)
    return sortie


def _apres_frontmatter(texte: str) -> int:
    """Position après un frontmatter YAML (`---` … `---`) en tête de fichier, sinon 0.

    Les SKILL.md (Agent Skills) doivent commencer par leur frontmatter : l'en-tête SPDX vient juste après.
    """
    if texte.startswith("---\n"):
        fin = texte.find("\n---\n", 4)
        if fin != -1:
            return fin + len("\n---\n")
    return 0


def est_conforme(texte: str) -> bool:
    debut = texte[_apres_frontmatter(texte):][:600]
    return f"SPDX-FileCopyrightText: {AUTEUR}" in debut and f"SPDX-License-Identifier: {LICENCE}" in debut


def signer(chemin: Path) -> bool:
    texte = chemin.read_text(encoding="utf-8")
    if est_conforme(texte):
        return False
    tete, texte = texte[:_apres_frontmatter(texte)], texte[_apres_frontmatter(texte):]
    if "SPDX-License-Identifier:" in texte[:600]:
        debut, reste = texte[:600], texte[600:]
        debut = re.sub(r"SPDX-FileCopyrightText:[^\n]*", f"SPDX-FileCopyrightText: {AUTEUR}", debut)
        debut = re.sub(r"SPDX-License-Identifier:[^\n]*", f"SPDX-License-Identifier: {LICENCE}", debut)
        chemin.write_text(tete + debut + reste, encoding="utf-8")
        return True
    bloc = entete(chemin.suffix or chemin.name)
    premiere, _, reste = texte.partition("\n")
    if premiere.startswith("#!"):           # le shebang doit rester en première ligne
        texte = f"{premiere}\n{bloc}{reste}"
    else:
        texte = bloc + texte
    chemin.write_text(tete + texte, encoding="utf-8")
    return True


if __name__ == "__main__":
    fichiers = a_signer()
    if "--verifier" in sys.argv:
        manquants = [f.relative_to(RACINE) for f in fichiers
                     if not est_conforme(f.read_text(encoding="utf-8"))]
        print(f"{len(fichiers) - len(manquants)}/{len(fichiers)} fichiers signés ({LICENCE})")
        for m in manquants:
            print("  manquant ou non conforme :", m)
        sys.exit(1 if manquants else 0)
    modifies = [f for f in fichiers if signer(f)]
    print(f"{len(modifies)} fichiers signés/mis à jour, {len(fichiers) - len(modifies)} déjà conformes")
