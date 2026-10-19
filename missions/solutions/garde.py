# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Exemple de politique en Python pour la mission 6 (copiez-le dans travail/garde.py).

`atelier verifier 6` appelle decider(commande, tache, modele) pour chaque commande de dev.
"""
import atelier as at

REGLAGE = at.ReglageGarde(seuil=0.4, verifs=("sortie", "secrets"))


def decider(commande: str, tache: str, modele) -> str:
    if commande.startswith("sudo "):          # une règle à moi : tout ce qui demande les droits root se valide
        action, _ = at.regles_garde(commande, REGLAGE)
        return action or "demander"
    action, _raison, _p = at.garde(modele, tache, commande, reglage=REGLAGE)
    return action
