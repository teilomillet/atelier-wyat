#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Lot de nuit : une requête JSON par ligne en entrée, une décision JSON par ligne en sortie (outil `wyat decide`).
# crontab -e   →   30 2 * * *  /chemin/wyat-atelier/integrations/lot_cron.sh entree.jsonl sortie.jsonl
set -euo pipefail
cd "$(dirname "$0")/.."
ENTREE=${1:-integrations/requete_exemple.jsonl}
SORTIE=${2:-integrations/decisions_du_lot.jsonl}
MOTEUR=$([ "$(uname -s)-$(uname -m)" = "Darwin-arm64" ] && echo mlx || echo torch)
.venv/bin/wyat decide "${WYAT_MODEL:-teilomillet/wyat-1-800m}" --backend "$MOTEUR" < "$ENTREE" > "$SORTIE"
echo "$(wc -l < "$SORTIE") décisions écrites dans $SORTIE"
