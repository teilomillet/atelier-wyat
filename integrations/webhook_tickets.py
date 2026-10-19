# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Service web minimal recevant un ticket et renvoyant la file de routage avec journal d'audit JSONL.

Lancer : .venv/bin/wyat serve teilomillet/wyat-1-800m --backend mlx      (le modèle, port 8000)
         .venv/bin/uvicorn integrations.webhook_tickets:app --port 8100  (ce service)
Essai  : curl -s localhost:8100/ticket -H 'Content-Type: application/json' -d '{"sujet": "Double débit", "corps": "Débité deux fois 54,90 €"}'
"""
from __future__ import annotations

import json
import time
from typing import Any, Final
import urllib.request

from fastapi import FastAPI

WYAT_URL: Final[str] = "http://127.0.0.1:8000/v1/decide"
OPTIONS: Final[dict[str, str]] = {
    "livraison": "Livraison : colis en retard, perdu, suivi bloqué, livré mais pas reçu",
    "retour": "Retour, échange ou remboursement d'un article déjà reçu",
    "paiement": "Paiement : carte refusée, double débit, prélèvement sans commande",
    "compte": "Compte client : connexion, mot de passe, adresse e-mail, données du compte",
    "autre": "Autre demande précise sans rapport avec une commande",
}
SEUIL: Final[float] = 0.5
app = FastAPI(title="Tri des tickets (wyat, local)")


@app.post("/ticket")
def ticket(entree: dict[str, Any]) -> dict[str, Any]:
    requete = {
        "task": "choice",
        "query": "Quel service doit traiter ce message ?",
        "candidates": [{"id": cle, "text": val} for cle, val in OPTIONS.items()],
        "context": f"{entree.get('sujet', '')}\n{entree.get('corps', '')}",
    }
    req = urllib.request.Request(
        WYAT_URL,
        json.dumps(requete).encode("utf-8"),
        {"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as reponse:
        decision = json.load(reponse)

    probas = sorted((float(p) for p in decision["probabilities"]), reverse=True)
    marge = probas[0] - probas[1]
    file_cible = str(decision["selected"]) if marge >= SEUIL else "humain"

    entree_journal = {
        "t": time.time(),
        "file": file_cible,
        "choix": decision["selected"],
        "marge": round(marge, 3),
        "model_id": decision["model_id"],
    }
    with open("decisions.log.jsonl", "a", encoding="utf-8") as journal:
        journal.write(json.dumps(entree_journal, ensure_ascii=False) + "\n")
    return {"file": file_cible, "choix": decision["selected"], "marge": round(marge, 3)}
