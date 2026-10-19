#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Régénère dataset/decisions_precalculees.jsonl avec le VRAI modèle (animateur, avant l'atelier) :
# exécute les notebooks, les exemples et toutes les vérifications de missions (dev et final),
# puis copie le cache local. Ce fichier sert au mode secours (WYAT_PRECALCULE=1) et aux tests.
set -euo pipefail
cd "$(dirname "$0")/.."
export WYAT_MODE=complet WYAT_PRECALCULE=0 WYAT_CACHE=1
rm -f .cache_atelier/decisions.jsonl
AVAIT_TRAVAIL=$([ -d travail ] && echo 1 || echo 0)
bash scripts/executer_notebooks.sh
for f in exemples/0*.py; do .venv/bin/python "$f" > /dev/null; done
T=$(mktemp -d)
.venv/bin/atelier preparer --dossier "$T/depart" > /dev/null
mkdir -p "$T/solution" && cp missions/solutions/* "$T/solution/"
for n in 1 2 3 4 5 6; do
  .venv/bin/atelier verifier "$n" --dossier "$T/depart" > /dev/null || true
  .venv/bin/atelier verifier "$n" --dossier "$T/solution" > /dev/null || true
done
for n in 4 5 6; do ATELIER_ANIMATEUR=1 .venv/bin/atelier verifier "$n" --final --dossier "$T/solution" > /dev/null || true; done
rm -f "$T/solution/garde.py"
.venv/bin/atelier verifier 6 --dossier "$T/solution" > /dev/null || true
ATELIER_ANIMATEUR=1 .venv/bin/atelier securite evaluer --jeu test > /dev/null
rm -rf "$T"
[ "$AVAIT_TRAVAIL" = 1 ] || rm -rf travail
cp .cache_atelier/decisions.jsonl dataset/decisions_precalculees.jsonl
echo "décisions pré-calculées : $(wc -l < dataset/decisions_precalculees.jsonl)"
