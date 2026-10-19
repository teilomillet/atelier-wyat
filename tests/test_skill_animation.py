# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Le skill d'animation (.agents/skills/animer-atelier-wyat) : présent pour chaque assistant, et son état de séance juste."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SKILL = RACINE / ".agents/skills/animer-atelier-wyat"


def test_skill_visible_par_chaque_assistant_et_frontmatter_valide():
    for lien in (".claude/skills/animer-atelier-wyat", ".github/skills/animer-atelier-wyat"):
        assert (RACINE / lien / "SKILL.md").resolve() == (SKILL / "SKILL.md").resolve(), lien
    texte = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert texte.startswith("---\nname: animer-atelier-wyat\ndescription:")
    for ref in ("references/scenes.md", "references/niveaux.md", "scripts/etat.py"):
        assert ref in texte and (SKILL / ref).exists(), ref


def test_etat_distingue_non_commence_modifie_et_test_ouvert(tmp_path):
    travail = tmp_path / "travail"
    travail.mkdir()
    departs = sorted((RACINE / "missions").glob("*/depart_*"))
    for d in departs:
        shutil.copy(d, travail / d.name.removeprefix("depart_"))
    politique = travail / "politique.toml"
    politique.write_text(politique.read_text(encoding="utf-8") + "\n# retouché\nseuil = 0.6\n", encoding="utf-8")
    (travail / ".scelle_ouvert.jsonl").write_text(json.dumps({"mission": 5, "date": "2026-10-19T10:00:00", "reussi": False}) + "\n")
    sortie = subprocess.run([sys.executable, str(SKILL / "scripts/etat.py"), "--dossier", str(travail)],
                            capture_output=True, text=True, check=True).stdout
    lignes = {l.split()[2]: l for l in sortie.splitlines() if l.strip().startswith("étape ") and len(l.split()) > 3}
    assert "modifié" in lignes["politique.toml"]
    assert "non commencé" in lignes["options.toml"]
    assert "étape 5 ouverte le 2026-10-19T10:00:00 : échouée" in sortie
