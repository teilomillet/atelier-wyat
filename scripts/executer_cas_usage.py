# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Exécute les cas d'usage avec le VRAI modèle et enregistre leur sortie (sortie_mlx.txt ou sortie_torch.txt).

Usage : .venv/bin/python scripts/executer_cas_usage.py [01 05 ...]   (sans argument : tous)
"""
import platform
import subprocess
import sys
import time
from pathlib import Path

CAS = Path(__file__).resolve().parent.parent / "cas_usage"
moteur = "mlx" if platform.system() == "Darwin" and platform.machine() == "arm64" else "torch"
choix = sys.argv[1:]
for dossier in sorted(p for p in CAS.iterdir() if p.is_dir() and p.name[:2].isdigit()):
    if choix and dossier.name[:2] not in choix:
        continue
    debut = time.time()
    r = subprocess.run([sys.executable, dossier / "cas.py"], capture_output=True, text=True)
    duree = time.time() - debut
    texte = r.stdout + (f"\n[ERREUR]\n{r.stderr[-2000:]}" if r.returncode else "")
    (dossier / f"sortie_{moteur}.txt").write_text(f"{texte.rstrip()}\n\n[{moteur}, {duree:.0f} s chargement compris]\n", "utf-8")
    print(f"== {dossier.name} ({duree:.0f} s)\n{texte.rstrip().splitlines()[-1] if texte.strip() else '(vide)'}", flush=True)
