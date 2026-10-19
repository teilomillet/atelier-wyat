# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Mesure la vitesse de wyat sur CET ordinateur et conseille un nombre de threads PyTorch.

Usage (depuis wyat-atelier/) : .venv/bin/python scripts/mesurer_vitesse.py
Durée : 1 à 3 min sur processeur. Les décisions sont identiques quel que soit le
nombre de threads (écarts d'arrondi ≈ 1e-5 sur les scores) ; seule la vitesse change.
"""
import os
import time

import atelier as at
from atelier import config

if at.BACKEND != "torch":
    m = at.charger_modele()
    raise SystemExit("Backend MLX : rien à régler (≈ 0,1 s par message).")

import torch
import wyat

brut = wyat.load(at.MODELE, device=at.DEVICE)
reqs = [at.requete(x, at.OPTIONS) for x in at.lire("dev_rapide.csv").message.head(6)]
brut.decide(reqs[0])  # préchauffage
coeurs = os.cpu_count() or 1
resultats = {}
for n in sorted({1, 2, 4, coeurs // 2 or 1, coeurs, torch.get_num_threads()}):
    if n > coeurs:
        continue
    torch.set_num_threads(n)
    t = time.time()
    for r in reqs:
        brut.decide(r)
    resultats[n] = (time.time() - t) / len(reqs)
    print(f"threads={n:<3} {resultats[n]:.2f} s par message", flush=True)
meilleur = min(resultats, key=resultats.get)
s = resultats[meilleur]
print(f"\nConseil : export WYAT_THREADS={meilleur}   (≈ {s:.2f} s par message)")
print(f"Mode rapide estimé : bloc 4 ≈ {60 * s / 60:.1f} min de calcul (3 × 20 messages), "
      f"bloc 5 ≈ {25 * s / 60:.1f} min (25 messages test, dev déjà en cache).")
print(f"Mode complet estimé : bloc 4 ≈ {3 * 63 * s / 60:.1f} min, bloc 5 ≈ {77 * s / 60:.1f} min.")
