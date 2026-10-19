# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Génère la fiche d'annotation (bloc 3) à partir de `dataset/labeling_15.csv`,
puis convertit chaque fiche Markdown de `docs/fiches/` en HTML et en PDF."""
from __future__ import annotations

import csv
from pathlib import Path
import shutil
import subprocess

import markdown

RACINE = Path(__file__).resolve().parents[1]
FICHES = RACINE / "docs" / "fiches"

with (RACINE / "dataset" / "labeling_15.csv").open(encoding="utf-8") as fichier:
    lignes_csv = list(csv.DictReader(fichier))

lignes = [
    "<!--",
    "SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet",
    "SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0",
    "-->",
    "# Bloc 3 — Fiche d'annotation (15 messages)",
    "",
    "Nom ou numéro d'annotateur (A1…A10) : ____________",
    "",
    "Pour chaque message, cochez **une seule** case : le service qui doit le traiter. "
    "Ne discutez pas avec vos voisins avant d'avoir fini : on mesure justement nos désaccords.",
    "",
    "*Messages synthétiques (écrits par une IA pour l'atelier, relus) : aucun vrai client.*",
    "",
    "| N° | Message | Fact. | Tech. | Résil. | Livr. | Autre | Sûr ? (1-3) |",
    "|---:|---|:-:|:-:|:-:|:-:|:-:|:-:|",
]
for r in lignes_csv:
    lignes.append(f"| {r['numero']} | {r['message'].replace('|', '/')} | ☐ | ☐ | ☐ | ☐ | ☐ | |")
lignes.extend([
    "",
    "**Rappel des services** : *facturation* (factures, débits / prélèvements, remboursements, paiement) · "
    "*technique* (internet, wifi, box, TV, mobile, SIM, appli en panne) · *résiliation* (mettre fin à un contrat, une ligne, une option) · "
    "*livraison* (commande, colis, suivi, retour de matériel) · *autre* (changement d'offre, déménagement, coordonnées, réclamation, info).",
    "",
    "Colonne « Sûr ? » : 1 = j'hésite, 3 = évident.",
])
(FICHES / "fiche_bloc3_annotation.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")

CSS = """body{font-family:-apple-system,Helvetica,Arial,sans-serif;font-size:10pt;max-width:780px;margin:16px auto;line-height:1.35}
table{border-collapse:collapse;width:100%}td,th{border:1px solid #999;padding:4px 6px;vertical-align:top;height:24px}
h1{font-size:18pt}h2{font-size:13pt;margin-top:18px}.box{border:1px solid #999;min-height:60px}
@page{size:A4;margin:14mm}"""

candidats_chrome = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
)
chrome = next((p for p in candidats_chrome if p and Path(p).exists()), None)

for md in sorted(FICHES.glob("*.md")):
    html = FICHES / f"{md.stem}.html"
    body = markdown.markdown(md.read_text(encoding="utf-8"), extensions=["tables"])
    html.write_text(
        f"<!doctype html><html lang='fr'><meta charset='utf-8'><style>{CSS}</style><body>{body}</body></html>",
        encoding="utf-8",
    )
    if chrome:
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f"--print-to-pdf={FICHES / (md.stem + '.pdf')}",
                html.as_uri(),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    print("fiche :", md.name, "→", "html + pdf" if chrome else "html (pas de Chrome : imprimez le HTML)")
