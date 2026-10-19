#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Exécute tous les notebooks de haut en bas et range les copies exécutées dans notebooks/executes/
# (ou dans le dossier donné par SORTIE=..., relatif à notebooks/).
# Les variables WYAT_BACKEND, WYAT_MODE, WYAT_CACHE, WYAT_PRECALCULE... sont transmises aux notebooks.
set -euo pipefail
cd "$(dirname "$0")/../notebooks"
SORTIE="${SORTIE:-executes}"
for nb in bloc1_demo bloc3_accord_annotateurs bloc4_lancer_wyat bloc5_mesurer_et_choisir bloc6_securite_et_limites; do
  start=$(date +%s)
  ../.venv/bin/jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=1800 \
      --ExecutePreprocessor.kernel_name=atelier-wyat --output-dir "$SORTIE" --output "${nb}_execute" "$nb.ipynb"
  echo "$nb : $(( $(date +%s) - start )) s"
done
