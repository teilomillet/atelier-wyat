#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Installation de l'atelier (Mac Apple Silicon, Linux, ou Windows via WSL).
#   Mac arm64           → wyat[mlx]       (GPU Apple, ≈ 0,15 s par message)
#   Linux / autres      → wyat[inference] (PyTorch ; roues CPU, ≈ 1 s par message sur 8 cœurs récents)
#   Linux + GPU NVIDIA  → WYAT_CUDA=1 bash scripts/installer.sh
set -euo pipefail
command -v uv >/dev/null || { echo "Installez uv d'abord : curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
OS="$(uname -s)"
ARCH="$(uname -m)"
uv venv --python 3.12 .venv
if [[ "$OS" == "Darwin" && "$ARCH" == "arm64" ]]; then
  echo "Mac Apple Silicon : moteur MLX"
  uv pip install --python .venv/bin/python "wyat[mlx,server]==0.1.2"
elif [[ "${WYAT_CUDA:-0}" == "1" ]]; then
  echo "$OS $ARCH avec GPU NVIDIA : PyTorch CUDA"
  uv pip install --python .venv/bin/python "wyat[inference,server]==0.1.2"
else
  echo "$OS $ARCH : PyTorch sur processeur (roues CPU)"
  uv pip install --python .venv/bin/python torch --index-url https://download.pytorch.org/whl/cpu
  uv pip install --python .venv/bin/python "wyat[inference,server]==0.1.2"
fi
uv pip install --python .venv/bin/python -e .
.venv/bin/python -m ipykernel install --prefix "$PWD/.venv" --name atelier-wyat --display-name "Python (atelier wyat)"
echo "Téléchargement du modèle (≈ 1,82 Go, vérifié par empreinte, une seule fois) :"
.venv/bin/wyat download
echo "Vérification express :"
.venv/bin/atelier info --vitesse
.venv/bin/atelier decider "On m'a prélevé deux fois ce mois-ci"
.venv/bin/atelier preparer
echo "OK. Trois façons de travailler :"
echo "  commande : source .venv/bin/activate && atelier --help"
echo "  scripts  : .venv/bin/python exemples/01_une_decision_wyat.py"
echo "  notebooks: .venv/bin/jupyter lab notebooks/"
