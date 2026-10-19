# SPDX-FileCopyrightText: 2026 Teïlo Millet - teilomillet
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Construit le jeu de données SYNTHÉTIQUE de l'atelier.

Tous les messages ci-dessous ont été écrits par une IA (Grok Bot) pour l'atelier,
puis relus. Aucun message réel de client. « Lumio » est un opérateur fictif.
Colonnes : id, message, label (étiquette de référence), labels_acceptables
(étiquettes défendables, séparées par |), difficulte (facile / ambigu / multi / piege), note.

Usage : python scripts/construire_dataset.py   (écrit dans dataset/)
"""
import csv
import random
from pathlib import Path

F, T, R, L, A = "facturation", "technique", "resiliation", "livraison", "autre"
# (message, label, autres étiquettes acceptables, difficulté, note)
M = [
 # ---------------- facturation ----------------
 ("Bonjour, j'ai été prélevé deux fois de 29,99 € ce mois-ci, pouvez-vous me rembourser le doublon ?", F, "", "facile", ""),
 ("Ma facture d'octobre est à 54 € alors que mon forfait est à 34,99. C'est quoi ces 20 € en plus ??", F, "", "facile", ""),
 ("Je n'arrive pas à télécharger ma facture en PDF dans l'espace client, le bouton ne fait rien.", F, T, "ambigu", "objet = facture, cause = bug"),
 ("comment je change mon RIB pour les prélèvements", F, "", "facile", "informel"),
 ("vous m'avez débité 9,99€ pour une option streaming que j'ai jamais demandée", F, "", "facile", ""),
 ("Bonsoir, le prélèvement a été rejeté par ma banque, je risque une coupure ? je peux payer par carte ?", F, "", "facile", ""),
 ("J'attends toujours le remboursement promis par votre conseiller il y a 3 semaines (geste commercial de 15 €).", F, "", "facile", ""),
 ("Pourquoi ma facture augmente de 3 € à partir de janvier ? On m'avait dit prix bloqué 2 ans.", F, "", "facile", ""),
 ("Bjr je voudrais recevoir mes factures par courrier et pas par mail", F, A, "ambigu", ""),
 ("j'ai payé la caution du décodeur 49€ et je l'ai rendu, quand est-ce que je suis remboursé", F, L, "multi", "retour matériel + remboursement"),
 ("Erreur sur ma facture : vous facturez 2 lignes mobiles alors que j'en ai qu'une.", F, "", "facile", ""),
 ("Bonjour, je souhaiterais un échéancier pour régler ma facture de 180 € en plusieurs fois, je suis en difficulté ce mois-ci.", F, "", "facile", ""),
 ("Le prélèvement de ce mois n'a pas eu lieu, est-ce normal ? Je ne veux pas avoir de frais de retard.", F, "", "facile", ""),
 ("hors forfait de 37 euros pour des appels vers la Belgique?? j'étais en vacances, c'est censé être inclus dans l'UE", F, "", "facile", ""),
 ("Pouvez-vous me renvoyer une facture au nom de ma société avec le numéro de TVA ? C'est pour ma compta.", F, "", "facile", ""),
 ("J'ai résilié en août et vous continuez de me prélever !!!! 3 mois de suite", F, R, "multi", "mot « résilié » mais demande = argent"),
 ("Je ne comprends rien à ma facture, il y a une ligne 'régularisation' de -12 € puis +18 €", F, "", "facile", ""),
 ("la promo -50% sur 6 mois n'apparaît pas sur ma facture", F, "", "facile", ""),
 ("Est-ce que je peux changer la date de prélèvement du 5 au 15 du mois ? je suis payé le 10", F, "", "facile", ""),
 ("Remboursement des frais de mise en service svp, c'était offert normalement", F, "", "facile", ""),
 ("On m'a facturé des frais de résiliation alors que je suis parti à cause de vos coupures à répétition", F, R, "multi", "frais contestés après départ"),
 ("jai recu un sms disant que mon paiement a échoué, mais la banque dit que tout est ok. arnaque ?", F, A, "ambigu", "peut être du hameçonnage"),
 ("Merci de m'envoyer le détail des communications du mois de septembre.", F, "", "facile", ""),
 ("J'ai été débité de 120 € pour le téléphone alors que je l'ai renvoyé sous 14 jours", F, L, "multi", ""),
 ("Facture impayée selon vous mais j'ai bien payé par virement le 3, voici la référence : VIR-88123", F, "", "facile", ""),
 ("Pourquoi je paie encore la location de la box alors que j'utilise la mienne ?", F, "", "facile", ""),
 ("c'est quoi les 2€ 'service plus' sur ma facture, j'ai jamais souscrit", F, "", "facile", ""),
 ("Je veux un avoir pour les 5 jours sans internet de la semaine dernière", F, T, "multi", "dédommagement d'une panne"),
 ("Ma carte bancaire a expiré, comment mettre à jour le moyen de paiement ?", F, "", "facile", ""),
 ("Votre appli m'affiche 0 € à payer mais j'ai reçu une relance par courrier pour 64 €", F, "", "facile", ""),
 ("Est-il possible d'avoir une facture rectifiée, le nom est mal orthographié (Lefèbvre et pas Lefebvre)", F, "", "facile", ""),
 ("Prélèvement SEPA de 0,01 € ?? c'est quoi ce truc", F, "", "facile", ""),
 ("Bonjour, double problème : ma box ne marche plus ET vous m'avez prélevé 2 fois. Commencez par me rembourser.", F, T, "multi", "le client donne la priorité"),
 ("J'ai renvoyé la box il y a un mois et vous me réclamez encore 150€ de pénalité de non-restitution", F, L, "multi", ""),
 ("Je suis malvoyant, existe-t-il des factures en gros caractères ?", F, A, "ambigu", ""),
 ("Bonjour, je constate un débit de 89,90 € de votre part le 12 alors que je n'ai rien commandé.", F, "", "facile", ""),
 ("mon forfait est passé de 15 à 20€ sans prévenir c normal ??", F, "", "facile", "informel, fautes"),
 # ---------------- technique ----------------
 ("Plus d'internet depuis ce matin, la box clignote rouge.", T, "", "facile", ""),
 ("la fibre rame à mort le soir, 3 Mb/s au lieu de 500", T, "", "facile", "informel"),
 ("Mon téléphone n'a plus de réseau depuis la mise à jour, il affiche 'SOS uniquement'", T, "", "facile", ""),
 ("Le décodeur TV reste bloqué sur l'écran de démarrage", T, "", "facile", ""),
 ("Je n'arrive pas à me connecter à l'espace client, mot de passe refusé alors que je l'ai réinitialisé 2 fois", T, "", "facile", ""),
 ("Comment je change le nom et le mot de passe du wifi ?", T, "", "facile", ""),
 ("appels coupés au bout de 30 secondes à chaque fois, c insupportable", T, "", "facile", "informel"),
 ("Ma nouvelle carte SIM n'est pas activée, ça fait 48h", T, "", "facile", ""),
 ("Le wifi ne passe pas à l'étage, vous avez des répéteurs ?", T, A, "ambigu", "problème + question commerciale"),
 ("Depuis l'orage d'hier la box ne s'allume plus du tout", T, "", "facile", ""),
 ("Impossible d'envoyer des MMS", T, "", "facile", ""),
 ("La TV pixelise sur toutes les chaînes HD", T, "", "facile", ""),
 ("l'appli Lumio plante dès que j'ouvre l'onglet factures", T, F, "piege", "mot « factures » mais c'est un bug"),
 ("Ma ligne fixe ne sonne plus, les gens tombent direct sur la messagerie", T, "", "facile", ""),
 ("Le technicien devait venir hier entre 8h et 12h pour le raccordement fibre, personne n'est venu.", T, A, "ambigu", ""),
 ("Je suis au Maroc et le roaming ne marche pas alors que je l'ai activé", T, "", "facile", ""),
 ("Mon débit montant est de 0,2 Mbps, je ne peux plus faire de visio pour le télétravail", T, "", "facile", ""),
 ("Comment brancher la box sur la prise fibre ? il y a deux prises dans le salon", T, "", "facile", ""),
 ("eSIM : le QR code ne fonctionne pas, il dit 'code non valide'", T, "", "facile", ""),
 ("La box redémarre toute seule toutes les 10 minutes depuis la mise à jour de mardi.", T, "", "facile", ""),
 ("Je ne reçois plus les SMS de ma banque pour valider mes paiements", T, "", "piege", "mot « paiements » mais c'est la réception SMS"),
 ("Mon internet coupe tous les soirs vers 21h, je vais résilier si ça continue", T, R, "multi", "menace conditionnelle"),
 ("Le replay ne fonctionne plus sur le décodeur, message erreur E-204", T, "", "facile", ""),
 ("Bonjour, le voyant 'fibre' est éteint sur ma box, pourtant le câble est bien branché.", T, "", "facile", ""),
 ("Est-ce que la box est compatible wifi 7 ?", T, A, "ambigu", "question d'information"),
 ("ma ligne mobile a été suspendue sans raison, je peux plus appeler", T, F, "ambigu", "souvent lié à un impayé"),
 ("Je n'entends pas mes correspondants, mais eux m'entendent", T, "", "facile", ""),
 ("la messagerie vocale me demande un code que je ne connais pas", T, "", "facile", ""),
 ("Mon portable chauffe et la batterie se vide depuis que la 5G est activée", T, "", "facile", ""),
 ("Pouvez-vous débloquer mon téléphone (désimlockage) ? IMEI 35-209900-176148-1", T, A, "ambigu", ""),
 ("Le contrôle parental ne bloque rien du tout, mes enfants accèdent à tout", T, "", "facile", ""),
 ("Netflix ne se lance plus sur le décodeur", T, "", "facile", ""),
 ("jarrive pa a me conecter au wifi avec mon nouvo ordi, ca di mot de passe incorect", T, "", "facile", "fautes"),
 ("Le débit est bon en filaire mais nul en wifi", T, "", "facile", ""),
 ("Transfert d'appel impossible à désactiver, tous mes appels partent vers un ancien numéro", T, "", "facile", ""),
 ("Mon téléphone reçu hier ne s'allume pas du tout, sorti du carton", T, L, "ambigu", "produit défectueux à la livraison"),
 ("Internet coupé depuis une semaine, je ne paierai pas ce mois-ci et je réfléchis à partir", T, "facturation|resiliation", "multi", "trois intentions"),
 ("Bonjour, mon décodeur affiche « pas de signal » sur la TV depuis que j'ai déplacé le meuble.", T, "", "facile", ""),
 # ---------------- résiliation ----------------
 ("Je souhaite résilier mon abonnement fibre, je déménage à l'étranger.", R, "", "facile", ""),
 ("comment on résilie ?", R, "", "facile", ""),
 ("Bonjour, merci de mettre fin à mon contrat mobile au 30 novembre.", R, "", "facile", ""),
 ("J'ai trouvé moins cher ailleurs, je veux partir. Quels sont les frais ?", R, F, "multi", ""),
 ("Je voudrais résilier la ligne de mon fils, il a maintenant son propre forfait", R, "", "facile", ""),
 ("Je veux arrêter l'option TV mais garder internet", R, A, "ambigu", "résiliation d'une option seulement"),
 ("Stop. Je pars chez la concurrence. Envoyez-moi le RIO.", R, "", "facile", ""),
 ("Est-ce que je peux résilier sans frais avant la fin des 12 mois d'engagement si je perds mon emploi ?", R, "", "facile", ""),
 ("Lettre de résiliation envoyée en recommandé le 2 octobre, toujours aucune confirmation", R, "", "facile", ""),
 ("j'en ai marre de vos pannes, je résilie, c'est fini", R, T, "multi", ""),
 ("Mon père est en EHPAD, je souhaite résilier sa ligne fixe", R, "", "facile", ""),
 ("Bonjour, je m'installe chez ma compagne qui est déjà chez vous, je n'ai plus besoin de ma box", R, A, "ambigu", "résiliation implicite"),
 ("Résiliation svp. Contrat n° LM-448812.", R, "", "facile", ""),
 ("Je veux annuler ma commande passée hier, j'ai changé d'avis", R, L, "ambigu", "rétractation d'une commande"),
 ("Comment désactiver le renouvellement automatique de l'abonnement streaming ?", R, "", "facile", ""),
 ("Je voudrais savoir combien de temps il me reste d'engagement avant de pouvoir partir", R, A, "ambigu", ""),
 ("vous pouvez couper mon abonnement à la fin du mois merci", R, "", "facile", "« couper » = résilier"),
 ("Je résilie suite à votre hausse de prix, conformément à mon droit de résiliation sans frais.", R, F, "multi", ""),
 ("Après 12 ans chez vous je m'en vais, mais je veux garder mon numéro de portable", R, "", "facile", ""),
 ("Suite au décès de ma mère, je dois résilier son abonnement. Quels justificatifs ?", R, "", "facile", ""),
 ("Je ne veux plus de la ligne fixe, je n'utilise que le mobile", R, "", "facile", ""),
 ("Annulez tout. Je ne veux plus entendre parler de Lumio.", R, "", "facile", ""),
 ("Je suis en période de rétractation (souscrit il y a 5 jours), je veux annuler.", R, "", "facile", ""),
 ("Bonjour, ma box internet ne me sert plus depuis que j'ai la 5G, comment arrêter ?", R, "", "facile", ""),
 # ---------------- livraison ----------------
 ("Ma commande de téléphone n'est toujours pas arrivée, ça fait 10 jours.", L, "", "facile", ""),
 ("Le colis est marqué livré mais je n'ai rien reçu", L, "", "facile", ""),
 ("Numéro de suivi svp pour ma nouvelle box", L, "", "facile", ""),
 ("Le livreur a laissé le colis chez un voisin que je ne connais pas", L, "", "facile", ""),
 ("J'ai reçu un iPhone 15 au lieu du 16 commandé", L, "", "facile", ""),
 ("Colis abîmé, la boîte de la box était écrasée, je l'ai refusé. Et maintenant ?", L, "", "facile", ""),
 ("Comment je renvoie l'ancien décodeur ? vous m'avez envoyé une étiquette ?", L, "", "facile", ""),
 ("Est-ce que je peux me faire livrer au bureau plutôt qu'à la maison ?", L, "", "facile", ""),
 ("la carte sim devait arriver par courrier il y a une semaine", L, "", "facile", ""),
 ("Relais colis fermé définitivement, comment récupérer mon colis ?", L, "", "facile", ""),
 ("Il manque le câble d'alimentation dans le carton de la box", L, T, "ambigu", ""),
 ("Je ne serai pas là jeudi pour la livraison, on peut décaler ?", L, "", "facile", ""),
 ("Vous m'avez envoyé 2 box, je fais quoi de la deuxième ?", L, "", "facile", ""),
 ("Commande n°CMD-77120 bloquée en 'préparation' depuis 5 jours", L, "", "facile", ""),
 ("Le point relais dit que le colis est reparti chez vous", L, "", "facile", ""),
 ("Bonjour, livraison prévue aujourd'hui mais toujours rien à 19h. Le livreur passe encore ?", L, "", "facile", ""),
 ("le transporteur dit adresse introuvable, alors que c'est la bonne adresse", L, "", "facile", ""),
 ("Ma commande de répéteur wifi est arrivée sans la notice", L, T, "ambigu", ""),
 ("Est-ce que vous livrez en Corse ? et combien de temps ?", L, "", "facile", ""),
 ("Je veux échanger le téléphone reçu, la couleur ne me plaît pas", L, "", "facile", ""),
 ("La coque était dans ma commande mais elle n'est pas dans le colis", L, "", "facile", ""),
 ("Retour du modem : le bureau de poste refuse l'étiquette, code-barres illisible", L, "", "facile", ""),
 ("J'ai déménagé entre-temps, est-ce que je peux changer l'adresse de livraison de ma commande en cours ?", L, A, "ambigu", ""),
 ("vous avez livré ma box chez mon ancienne adresse !!", L, "", "facile", ""),
 ("Quand vais-je recevoir le téléphone offert avec mon abonnement ?", L, "", "facile", ""),
 ("Le livreur exige une signature mais je ne suis jamais là en journée", L, "", "facile", ""),
 ("Bonsoir, résiliation de ma box ok mais comment je renvoie le matériel ?", L, R, "multi", "la question porte sur le renvoi"),
 ("Bonjour, ma commande peut-elle être livrée avant samedi ? C'est pour un cadeau.", L, "", "facile", ""),
 ("colis pas reçu", L, "", "facile", "très court"),
 # ---------------- autre ----------------
 ("Je déménage le mois prochain, comment transférer ma box à ma nouvelle adresse ?", A, "", "facile", "déménagement ≠ résiliation"),
 ("Je veux changer de forfait mobile pour un 100 Go", A, "", "facile", "changement d'offre"),
 ("Votre conseillère au téléphone a été très désagréable, je veux faire une réclamation.", A, "", "facile", ""),
 ("Bonjour, est-ce que vous recrutez des techniciens à Lyon ?", A, "", "piege", "mot « techniciens » mais hors support"),
 ("Je souhaite modifier mon adresse mail de contact", A, "", "facile", ""),
 ("Comment je fais pour parrainer un ami qui veut s'abonner ?", A, "", "facile", ""),
 ("Je veux exercer mon droit d'accès RGPD : quelles données avez-vous sur moi ?", A, "", "facile", ""),
 ("merci pour votre aide hier, tout fonctionne !", A, "", "facile", ""),
 ("Avez-vous une boutique à Rennes ?", A, "", "facile", ""),
 ("Je voudrais ajouter une ligne mobile pour ma fille", A, "", "facile", ""),
 ("bonjour", A, "", "ambigu", "aucune intention"),
 ("Quels sont vos horaires d'ouverture du service client ?", A, "", "facile", ""),
 ("Le numéro qui m'appelle 10 fois par jour se présente comme Lumio, c'est vous ?", A, "", "facile", ""),
 ("Je voudrais passer mon contrat au nom de mon mari", A, "", "facile", ""),
 ("Puis-je récupérer mon ancien numéro de fixe que j'avais il y a 2 ans ?", A, T, "ambigu", ""),
 ("Votre pub à la télé dit fibre à 19,99 €, j'y ai droit en tant que client ?", A, F, "ambigu", "offre commerciale"),
 ("Je fais une enquête pour mon école sur les opérateurs, puis-je vous poser quelques questions ?", A, "", "facile", ""),
 ("SVP rappelez-moi au 06 12 34 56 78, c'est urgent", A, "", "ambigu", "aucun sujet : à escalader"),
 ("J'ai un litige avec vous depuis 3 mois, je vais saisir le médiateur des communications électroniques.", A, "", "ambigu", "contentieux"),
 ("Combien coûte l'option TV en plus de mon forfait fibre ?", A, F, "ambigu", "question de prix ≠ facture"),
 ("je suis étudiant, il y a une réduction ?", A, F, "ambigu", "offre commerciale"),
 ("Est-ce que je peux mettre mon abonnement en pause pendant 6 mois à l'étranger au lieu de résilier ?", A, R, "piege", "mot « résilier » mais demande = suspension"),
 ("Bonjour, mon conjoint est décédé, je voudrais transférer le contrat à mon nom et que les prélèvements sur son compte s'arrêtent.", A, "facturation|resiliation", "multi", "transfert de titulaire"),
 ("Je voudrais résilier... non attendez, en fait je veux juste passer au forfait moins cher.", A, R, "piege", "le client se corrige"),
 ("Je n'arrive pas à joindre le service client par téléphone, 45 min d'attente à chaque fois", A, "", "facile", ""),
 ("Bonjour, j'ai une question.", A, "", "ambigu", "aucune intention"),
 ("lol", A, "", "ambigu", "bruit"),
]

def main():
    root = Path(__file__).resolve().parents[1] / "dataset"
    rows = []
    for i, (msg, lab, alt, diff, note) in enumerate(M, 1):
        acc = [lab] + [x for x in alt.split("|") if x]
        rows.append({"id": f"m{i:03d}", "message": msg, "label": lab,
                     "labels_acceptables": "|".join(dict.fromkeys(acc)),
                     "difficulte": diff, "note": note})
    assert len({r["message"] for r in rows}) == len(rows), "doublon"
    rng = random.Random(2026)
    rng.shuffle(rows)
    # 15 messages pour l'exercice d'annotation : 9 faciles/pièges + 6 ambigus/multi, toutes classes
    lab15, rest = [], []
    want = {"facile": 8, "piege": 2, "ambigu": 3, "multi": 2}
    for r in rows:
        key = r["difficulte"]
        if want.get(key, 0) > 0 and sum(x["label"] == r["label"] for x in lab15) < 3:
            want[key] -= 1
            lab15.append(r)
        else:
            rest.append(r)
    # reste : stratifié par classe, ~45 % dev / 55 % test scellé
    dev, test = [], []
    for c in (F, T, R, L, A):
        cls = [r for r in rest if r["label"] == c]
        k = round(len(cls) * 0.45)
        dev += cls[:k]
        test += cls[k:]
    rng.shuffle(dev)
    rng.shuffle(test)
    cols = ["id", "message", "label", "labels_acceptables", "difficulte", "note"]
    def write(name, data, fields):
        with open(root / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(data)
    lab15 = sorted(lab15, key=lambda r: r["id"])
    for n, r in enumerate(lab15, 1):
        r["numero"] = n
    write("labeling_15.csv", lab15, ["numero", "id", "message"])
    write("labeling_15_corrige.csv", lab15, ["numero", "id"] + cols[1:])
    write("dev.csv", dev, cols)
    write("test_scelle.csv", test, cols)
    write("tous_les_messages.csv", sorted(rows, key=lambda r: r["id"]), cols)
    from collections import Counter
    for name, d in (("labeling_15", lab15), ("dev", dev), ("test_scelle", test)):
        print(name, len(d), dict(Counter(r["label"] for r in d)), dict(Counter(r["difficulte"] for r in d)))

if __name__ == "__main__":
    main()
