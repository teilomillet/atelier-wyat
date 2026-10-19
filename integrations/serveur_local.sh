#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Serveur HTTP local de wyat, accessible depuis cette machine seulement (127.0.0.1). Port 8790 par défaut (WYAT_PORT pour changer).
set -euo pipefail
cd "$(dirname "$0")/.."
MOTEUR=$([ "$(uname -s)-$(uname -m)" = "Darwin-arm64" ] && echo mlx || echo torch)
exec .venv/bin/wyat serve "${WYAT_MODEL:-teilomillet/wyat-1-800m}" --backend "$MOTEUR" --host 127.0.0.1 --port "${WYAT_PORT:-8790}"
