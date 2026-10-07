# Fichier de la formation : ne pas modifier.
"""Tests du comportement attendu de sync_tarifs.py.

Ils doivent rester au vert après le patch de sécurité : corriger une faille
ne doit pas changer ce que le script fait pour un fichier légitime.
Vos propres tests vont dans tests/test_failles.py.
Lancement : python3 -m unittest
"""
import os
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sync_tarifs  # noqa: E402

FICHIER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "data", "tarifs_materiaux_riviere.csv")


class TestSynchronisation(unittest.TestCase):
    def setUp(self):
        self.dossier = tempfile.TemporaryDirectory()
        self.connexion = sync_tarifs.ouvrir_base(os.path.join(self.dossier.name, "t.db"))

    def tearDown(self):
        self.connexion.close()
        self.dossier.cleanup()

    def test_importe_toutes_les_lignes(self):
        self.assertEqual(sync_tarifs.importer(FICHIER, self.connexion), 8)

    def test_applique_la_formule_de_prix(self):
        sync_tarifs.importer(FICHIER, self.connexion)
        self.assertEqual(sync_tarifs.chercher("LAINE-R5", self.connexion),
                         [("LAINE-R5", "Laine de verre R5, rouleau", 38.64)])

    def test_prix_sans_remise(self):
        sync_tarifs.importer(FICHIER, self.connexion)
        self.assertEqual(sync_tarifs.chercher("PLAQ-BA13", self.connexion)[0][2], 9.8)

    def test_reference_inconnue(self):
        sync_tarifs.importer(FICHIER, self.connexion)
        self.assertEqual(sync_tarifs.chercher("INCONNUE", self.connexion), [])

    def test_libelle_avec_apostrophe(self):
        chemin = os.path.join(self.dossier.name, "a.csv")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write("reference;libelle;prix_ht;remise;fiche_url;fiche_nom\n"
                    "PEINT-BL;Peinture d'intérieur;64.00;0;;\n")
        sync_tarifs.importer(chemin, self.connexion)
        self.assertEqual(sync_tarifs.chercher("PEINT-BL", self.connexion)[0][1], "Peinture d'intérieur")


if __name__ == "__main__":
    unittest.main()
