# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Cas 15 — Garde-fou pour du code généré : ce script touche-t-il à des fichiers hors du projet ou envoie-t-il des données ? (wyat + règles)"""
import csv
import os
import platform
import re
from pathlib import Path

import wyat

ICI = Path(__file__).parent
modele = wyat.load(os.environ.get("WYAT_MODEL", "teilomillet/wyat-1-800m"), backend="mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch")

QUESTION = ("Une fois exécuté, ce code supprime-t-il, écrase-t-il ou envoie-t-il vers l'extérieur des fichiers ou des données "
            "situés en dehors du dossier du projet ?")
MOTIFS = {   # les formats connus : au code
    "rm récursif hors projet": r"rm\s+-[a-z]*r[a-z]*f?\s+(/|~|\$HOME|\.\./)",
    "shutil.rmtree hors projet": r"rmtree\(\s*['\"](/|~)",
    "téléchargement exécuté": r"(curl|wget)[^|]*\|\s*(ba)?sh",
    "envoi réseau": r"requests\.(post|put)|curl\s+.*(-T|--upload-file|-d\s*@)|scp\s",
    "chemin système": r"/etc/|/usr/|C:\\\\Windows",
}

bilan = {"ecriture": [0, 0, 0], "verification": [0, 0, 0]}   # wyat seul, wyat + règles, total
with open(ICI / "donnees.csv", encoding="utf-8") as _f:
    _lignes = list(csv.DictReader(_f))
for l in _lignes:
    p = modele.decide(wyat.Request.noul(QUESTION, context=l["code"])).probability_true
    r = [nom for nom, motif in MOTIFS.items() if re.search(motif, l["code"])]
    seul, ensemble = p >= 0.5, bool(r) or p >= 0.5
    b = bilan[l["jeu"]]
    b[0] += seul == (l["attendu"] == "oui")
    b[1] += ensemble == (l["attendu"] == "oui")
    b[2] += 1
    print(f"{l['code'][:52].replace(chr(10), ' ⏎ '):<52} P {p:.2f} règles {r or '-'} → {'BLOQUER, relecture' if ensemble else 'exécuter'} (attendu {l['attendu']})")
print("\n" + " ; ".join(f"{j} : wyat seul {a}/{n}, wyat + règles {c}/{n}" for j, (a, c, n) in bilan.items()))
