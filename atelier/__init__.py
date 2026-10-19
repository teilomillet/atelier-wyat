# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Boîte à outils de l'atelier « Modèles de décision avec wyat ».

Trois façons de s'en servir : la commande `atelier` (voir `atelier --help`), vos propres scripts
(`import atelier as at`, voir exemples/), ou les notebooks (notebooks/). Tout tourne en local.

Fonctions principales ::

    m = at.charger_modele()                      # MLX, PyTorch CPU/CUDA, ou secours pré-calculé
    d = at.decider(m, "on m'a prélevé deux fois")  # une décision wyat
    dev = at.lire("dev")                          # jeux de données (version réduite en mode rapide)
    rapport, res = at.evaluer(m, dev, options)    # exactitude ligne par ligne + rapport wyat
    at.intervalle_bootstrap(res.correct)          # IC 95 %
    at.courbe_selective(rapport)                  # automatisation vs erreurs, par seuil
    at.kappa_fleiss(table)                        # accord entre annotateurs
    at.garde(m, tache, commande)                  # garde-fou de commandes (bloc 6)
"""
from __future__ import annotations

from . import config
from .donnees import lire, lire_secu
from .mesures import (accord, accord_moyen, courbe_selective, ece, evaluer, interpretation_kappa,
                      intervalle_bootstrap, kappa_cohen, kappa_fleiss, router, table_fiabilite)
from .modele import (DecisionNonPrecalculee, ModeleAtelier, charger_modele, decider, decider_lot,
                     duree_estimee, modele_id, probas, requete)
from .options import (OPTIONS, OPTIONS_EXERCICE, OPTIONS_FOURRE_TOUT, QUESTION, SERVICES, ecrire_options,
                      lire_options)
from .securite import (LISTE_BLANCHE, OPTIONS_ARNAQUE, OPTIONS_GARDE, OPTIONS_INJECTION, QUESTION_ARNAQUE,
                       QUESTION_GARDE, QUESTION_INJECTION, REGLES_REFUS, SIGNAUX_ARNAQUE, VERIFS_GARDE,
                       ReglageGarde, bilan_arnaques, bilan_garde, evaluer_arnaques, evaluer_garde, garde,
                       p_arnaque, p_injection, regles_garde, requete_arnaque, requete_garde, requetes_verifs,
                       signaux_arnaque)

__version__ = "1.0.0"


def __getattr__(nom: str):
    """Compatibilité : at.BACKEND, at.DEVICE, at.MODE_RAPIDE, at.MODELE (lus à chaque accès)."""
    valeurs = {"BACKEND": config.backend, "DEVICE": config.device, "MODE_RAPIDE": config.mode_rapide,
               "MODELE": config.modele}
    if nom in valeurs:
        return valeurs[nom]()
    raise AttributeError(nom)
