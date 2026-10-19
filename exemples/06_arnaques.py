# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Signaler les SMS / e-mails suspects, avec des questions oui / non pour expliquer l'alerte.

Lancer : .venv/bin/python exemples/06_arnaques.py
"""
from types import SimpleNamespace

import atelier as at

modele = at.charger_modele()
sms = SimpleNamespace(canal="SMS", expediteur="+33 7 56 12 84 90",
                      message="Colissimo : votre colis est en attente, des frais de 1,99 € sont à régler : colissimo-suivi-fr.info/r/8KQ")
p = at.p_arnaque(modele, sms.canal, sms.expediteur, sms.message)
print(f"P(frauduleux) = {p:.2f} →", "MESSAGE SUSPECT" if p >= 0.4 else "rien à signaler")
print("signaux :", at.signaux_arnaque(modele, sms))
