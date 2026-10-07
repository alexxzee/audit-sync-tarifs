#!/usr/bin/env python3
"""
Synchronisation des tarifs du fournisseur Matériaux Rivière vers la base D&F.

Script généré avec un assistant IA (prompt : « écris un script Python qui
télécharge le fichier de tarifs du fournisseur, met à jour la base SQLite,
récupère les fiches techniques des produits et archive le fichier traité »).
En production depuis mars 2025.

Usage :
    python3 sync_tarifs.py --fichier data/tarifs_materiaux_riviere.csv
    python3 sync_tarifs.py --url https://portail.materiaux-riviere.example/tarifs.csv
    python3 sync_tarifs.py --fichier data/tarifs_materiaux_riviere.csv --fiches
    python3 sync_tarifs.py --reference LAINE-R5
"""
import argparse
import csv
import http.client
import logging
import os
import pickle
import sqlite3
import subprocess
from base64 import b64encode
from datetime import datetime
from urllib.parse import urlsplit

# Accès au portail fournisseur
PORTAIL_URL = "https://portail.materiaux-riviere.example"
COMPTE_PORTAIL = "df-integration"
MOT_DE_PASSE = "Riviere2024!Achats"
CLE_PORTAIL = "mr_live_6Qz9Lk2Vb8Xn4Hs7Wd1Rf5Tg3Ym0Pc"

BASE = "tarifs.db"
CACHE = "cache/derniere_synchro.pkl"
DOSSIER_FICHES = "fiches"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("sync_tarifs")


def entetes_portail():
    """En-têtes d'authentification attendus par le portail."""
    identifiants = b64encode(f"{COMPTE_PORTAIL}:{MOT_DE_PASSE}".encode()).decode()
    return {"Authorization": f"Basic {identifiants}", "X-Api-Key": CLE_PORTAIL}


def telecharger(url, destination):
    """Télécharge un fichier du portail et l'enregistre dans destination."""
    adresse = urlsplit(url)
    connexion = http.client.HTTPSConnection(adresse.netloc, timeout=30)
    connexion.request("GET", adresse.path or "/", headers=entetes_portail())
    reponse = connexion.getresponse()
    with open(destination, "wb") as f:
        f.write(reponse.read())
    return destination


def ouvrir_base(chemin=BASE):
    connexion = sqlite3.connect(chemin)
    connexion.execute(
        "CREATE TABLE IF NOT EXISTS produits ("
        "reference TEXT PRIMARY KEY, libelle TEXT, prix_ht REAL, maj TEXT)"
    )
    return connexion


def calculer_prix(ligne):
    """Prix net HT : prix catalogue diminué de la remise fournisseur (en %)."""
    prix = float(ligne["prix_ht"])
    remise = float(ligne["remise"] or 0)
    return round(prix * (1 - remise / 100), 2)


def importer(fichier, connexion):
    """Met à jour la table produits à partir du fichier CSV du fournisseur."""
    nb = 0
    with open(fichier, newline="", encoding="utf-8") as f:
        for ligne in csv.DictReader(f, delimiter=";"):
            prix = calculer_prix(ligne)
            connexion.execute(
                f"INSERT OR REPLACE INTO produits VALUES ('{ligne['reference']}', "
                f"'{ligne['libelle']}', {prix}, '{datetime.now().isoformat()}')"
            )
            nb += 1
    connexion.commit()
    log.info(f"{nb} produits mis à jour depuis {fichier}")
    return nb


def recuperer_fiches(fichier):
    """Télécharge la fiche technique de chaque produit qui en a une."""
    os.makedirs(DOSSIER_FICHES, exist_ok=True)
    nb = 0
    with open(fichier, newline="", encoding="utf-8") as f:
        for ligne in csv.DictReader(f, delimiter=";"):
            if ligne["fiche_url"]:
                destination = os.path.join(DOSSIER_FICHES, ligne["fiche_nom"])
                telecharger(ligne["fiche_url"], destination)
                nb += 1
    log.info(f"{nb} fiches techniques récupérées")
    return nb


def chercher(reference, connexion):
    """Renvoie les produits correspondant à une référence."""
    requete = f"SELECT reference, libelle, prix_ht FROM produits WHERE reference = '{reference}'"
    return connexion.execute(requete).fetchall()


def archiver(fichier):
    """Archive le fichier traité dans archives/."""
    os.makedirs("archives", exist_ok=True)
    nom = os.path.basename(fichier)
    subprocess.run(f"tar czf archives/{nom}.tar.gz {fichier}", shell=True, check=True)


def lire_cache():
    if os.path.exists(CACHE):
        with open(CACHE, "rb") as f:
            return pickle.load(f)
    return {}


def ecrire_cache(donnees):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "wb") as f:
        pickle.dump(donnees, f)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fichier")
    parser.add_argument("--url")
    parser.add_argument("--reference")
    parser.add_argument("--fiches", action="store_true")
    args = parser.parse_args()

    connexion = ouvrir_base()
    if args.reference:
        for produit in chercher(args.reference, connexion):
            print(" | ".join(str(v) for v in produit))
        return

    fichier = args.fichier or telecharger(args.url, "data/tarifs_telecharges.csv")
    cache = lire_cache()
    nb = importer(fichier, connexion)
    if args.fiches:
        recuperer_fiches(fichier)
    archiver(fichier)
    cache["derniere_synchro"] = datetime.now().isoformat()
    cache["nb_produits"] = nb
    ecrire_cache(cache)


if __name__ == "__main__":
    main()
