# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Garde-fou de sécurité via le serveur HTTP local de wyat : appels d'outils d'un agent et e-mails signalés.

Le serveur :  .venv/bin/wyat serve "$WYAT_MODEL" --backend mlx --host 127.0.0.1 --port 8790   (ou ./integrations/serveur_local.sh)
Ce module  :  .venv/bin/python integrations/garde_http.py      (deux exemples, journal dans garde_http.log.jsonl)

Les politiques (`politique_appel`, `politique_email`) sont des fonctions pures : elles se testent sans modèle (`tests/test_garde_http.py`).
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import datetime
import json
import os
from pathlib import Path
import re
from typing import Any, Final, Literal
import urllib.request

ActionAppel = Literal["refuser", "confirmer", "executer"]
ActionEmail = Literal["classer", "analyste", "quarantaine"]

URL: Final[str] = os.environ.get("WYAT_URL", "http://127.0.0.1:8790/v1/decide")
JOURNAL: Final[Path] = Path(os.environ.get("GARDE_JOURNAL", "garde_http.log.jsonl"))
POLITIQUE: Final[str] = "garde-http v1"

CATEGORIE: Final[dict[str, str]] = {
    "rechercher_documents": "lecture",
    "lire_agenda": "lecture",
    "creer_brouillon": "ecriture",
    "envoyer_email": "externe",
    "virement": "externe",
    "supprimer_fichier": "irreversible",
}
DOMAINES_INTERNES: Final[tuple[str, ...]] = ("groupe-exemple.fr",)
INJECTION: Final[re.Pattern[str]] = re.compile(
    r"ignore[rz]? (toutes |les )?(tes |vos |les )?(instructions|consignes)|"
    r"ignore (all|previous)|tu es (désormais|maintenant)",
    re.IGNORECASE,
)


def p_vrai(question: str, contexte: Any) -> tuple[float, str]:
    """Pose une question oui / non au serveur local ; renvoie `(P(oui), model_id)`."""
    texte_ctx = contexte if isinstance(contexte, str) else json.dumps(contexte, ensure_ascii=False)
    corps = json.dumps({"task": "noul", "query": question, "context": texte_ctx}).encode("utf-8")
    requete = urllib.request.Request(URL, corps, {"Content-Type": "application/json"})
    with urllib.request.urlopen(requete, timeout=30) as reponse:
        d = json.load(reponse)
    proba = max(d["probabilities"]) if d["selected"] == "true" else min(d["probabilities"])
    return float(proba), str(d["model_id"])


def politique_appel(
    outil: str,
    arguments: Mapping[str, Any],
    p_concordance: float,
    seuil: float = 0.6,
) -> tuple[ActionAppel, str]:
    """Décision pure sur un appel d'outil : le code contrôle catégorie et destinataires, `wyat` la concordance."""
    categorie = CATEGORIE.get(outil)
    if categorie is None:
        return "refuser", "outil inconnu"

    destinataires = [
        adr.strip()
        for cle in ("a", "cc", "cci")
        for adr in str(arguments.get(cle, "")).split(",")
        if "@" in adr
    ]
    suffixes_internes = tuple(f"@{dom}" for dom in DOMAINES_INTERNES)
    externes = [adr for adr in destinataires if not adr.endswith(suffixes_internes)]

    if any(INJECTION.search(str(val)) for val in arguments.values()):
        return "refuser", "instruction suspecte dans les arguments"
    if p_concordance < seuil:
        return "refuser", f"appel non conforme à la demande (P = {p_concordance:.2f})"
    if externes:
        return "confirmer", f"destinataire externe : {', '.join(externes)}"
    if categorie in ("externe", "irreversible"):
        return "confirmer", f"outil {categorie}"
    return "executer", f"{categorie}, concordance {p_concordance:.2f}"


def politique_email(
    p_hameconnage: float,
    regles: Sequence[str],
    bas: float = 0.25,
    haut: float = 0.75,
) -> ActionEmail:
    """Trois issues : `classer`, `analyste` (zone grise : abstention), `quarantaine`."""
    if regles or p_hameconnage >= haut:
        return "quarantaine"
    return "analyste" if p_hameconnage >= bas else "classer"


def journaliser(**champs: Any) -> None:
    entree = {
        "horodatage": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "politique": POLITIQUE,
        **champs,
    }
    with JOURNAL.open("a", encoding="utf-8") as fichier:
        fichier.write(json.dumps(entree, ensure_ascii=False) + "\n")


def controler_appel(demande: str, outil: str, arguments: Mapping[str, Any]) -> ActionAppel:
    question = (
        "Cet appel d'outil fait-il exactement ce que l'utilisateur a demandé, "
        "avec le même destinataire, le même montant et la même cible ?"
    )
    contexte = {"demande_utilisateur": demande, "appel_propose": {"outil": outil, "arguments": dict(arguments)}}
    proba, modele_id = p_vrai(question, contexte)
    action, raison = politique_appel(outil, arguments, proba)
    journaliser(
        type="appel_outil",
        modele=modele_id[:16],
        demande=demande,
        outil=outil,
        arguments=dict(arguments),
        p=round(proba, 4),
        action=action,
        raison=raison,
    )
    return action


if __name__ == "__main__":
    print(
        controler_appel(
            "Envoie le compte rendu à Paul Martin",
            "envoyer_email",
            {"a": "paul.martin@groupe-exemple.fr", "objet": "Compte rendu"},
        )
    )
    print(
        controler_appel(
            "Envoie le compte rendu à Paul Martin",
            "envoyer_email",
            {"a": "p.martin.perso@protonmail.com", "objet": "Compte rendu"},
        )
    )
    print("journal :", JOURNAL.resolve())
