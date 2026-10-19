#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Garde-fou pour un agent de code (hook PreToolUse de Claude Code) : règles écrites + wyat via serveur local.

1. Lancer le serveur une fois :  .venv/bin/wyat serve teilomillet/wyat-1-800m --backend mlx   (ou torch)
2. Dans .claude/settings.json du projet :
   {"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command",
     "command": "python3 /chemin/wyat-atelier/integrations/hook_claude_code.py", "onFailure": "block"}]}]}}
Sortie : allow / ask / deny. Ce script n'utilise que la bibliothèque standard.
"""
from __future__ import annotations

import json
import re
import sys
from typing import Final, Literal, NoReturn
import urllib.request

DecisionHook = Literal["allow", "ask", "deny"]

SERVEUR: Final[str] = "http://127.0.0.1:8000/v1/decide"
LISTE_BLANCHE: Final[re.Pattern[str]] = re.compile(
    r"^(ls|pwd|cat [\w./-]+\.(py|md|txt|toml)|git (status|diff|log)|pytest)\b"
)
REFUS: Final[tuple[str, ...]] = (
    r"rm\s+-[a-z]*r[a-z]*f?\s+(/|~|\"?\$\w+\"?/?)(\s|$)",
    r"\|\s*(ba)?sh\b",
    r"git push .*--force",
    r"chmod -R 777",
    r"\.ssh/id_",
)


def _emettre_decision(action: DecisionHook, raison: str) -> NoReturn:
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": action,
            "permissionDecisionReason": raison,
        }
    }
    print(json.dumps(payload, ensure_ascii=False))
    sys.exit(0)


def main() -> NoReturn:
    entree = json.load(sys.stdin)
    tool_input = entree.get("tool_input", {})
    commande = str(tool_input.get("command", ""))
    if any(re.search(motif, commande) for motif in REFUS):
        _emettre_decision("deny", "règle écrite : commande interdite")
    if LISTE_BLANCHE.match(commande):
        _emettre_decision("allow", "liste blanche")

    requete = {
        "task": "choice",
        "query": "Un agent IA veut exécuter cette commande shell. Peut-il le faire sans demander ?",
        "candidates": [
            {
                "id": "sans_risque",
                "text": (
                    "On peut l'exécuter sans demander : elle ne fait que lire, "
                    "ou ne touche qu'au projet de façon réversible"
                ),
            },
            {
                "id": "a_valider",
                "text": (
                    "Un humain doit valider avant : elle supprime, écrase, publie, change des droits "
                    "ou une configuration, touche à la production, aux secrets, ou envoie des données"
                ),
            },
        ],
        "context": f"tâche : {tool_input.get('description', '')}\ncommande proposée par l'agent : {commande}",
    }
    try:
        req = urllib.request.Request(
            SERVEUR,
            json.dumps(requete).encode("utf-8"),
            {"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=20) as reponse:
            resultat = json.load(reponse)
    except OSError:
        _emettre_decision("ask", "serveur wyat injoignable : on demande")

    p_valider = float(resultat["probabilities"][1])
    action: DecisionHook = "ask" if p_valider >= 0.4 else "allow"
    _emettre_decision(action, f"wyat : P(à valider) = {p_valider:.2f}")


if __name__ == "__main__":
    main()
