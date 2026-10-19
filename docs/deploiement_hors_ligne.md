<!--
SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
-->
# Déploiement sur une machine sans réseau (réseau isolé, sur site)

1. **Sur une machine connectée**, préparez le paquet :
   ```sh
   ./scripts/installer.sh            # crée .venv et télécharge le modèle (≈ 1,82 Go, vérifié par empreinte)
   # roues Python pour la machine cible (même OS, même architecture, même version de Python) :
   python3.12 -m pip download . "wyat[inference,server]==0.1.2" torch \
       --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple -d roues/
   ```
   Le modèle est dans `~/.cache/wyat/wyat-1-800m/` (dossier `model/`, plus `LICENSE` et `NOTICE`, à conserver ensemble).
2. **Transférez** ce dépôt, l'environnement et le dossier du modèle par le support validé par votre politique de sécurité (station blanche, clé contrôlée). Vérifiez les empreintes : `shasum -a 256` sur les fichiers, comparées au fichier `FILES.sha256` du dépôt du modèle.
3. **Sur la machine isolée**, installez sans index (`uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python --no-index --find-links roues/ -e . "wyat[inference,server]==0.1.2" torch`), puis pointez vers le dossier local ; aucun nom de dépôt, donc aucun téléchargement possible :
   ```sh
   export WYAT_MODEL=/opt/modeles/wyat-1-800m/model
   .venv/bin/python cas_usage/25_documents_hors_ligne/cas.py      # coupe le réseau dans le processus, puis décide
   .venv/bin/wyat serve "$WYAT_MODEL" --backend torch --host 127.0.0.1 --port 8790   # service local, sans exposition
   ```
4. **Journal** local (voir cas 14 et 21) ; rotation et conservation selon votre politique.

Points de vigilance : `wyat.load("teilomillet/wyat-1-800m")` télécharge si le cache est absent ; en environnement isolé, utilisez **toujours un chemin**. Sous Linux, PyTorch CPU suffit (pas de GPU requis). Le cas 25 montre la proposition d'un niveau de manipulation : la **classification** d'un document reste une décision d'une autorité habilitée.
