# audit-sync-tarifs

Script de synchronisation des tarifs du fournisseur Matériaux Rivière vers la base de Delmas & Fournier. **Il a été généré avec un assistant IA et tourne en production.** Sophie Lambert (RSSI de Néotis) en commande l’audit.

Toutes les clés, tous les mots de passe et toutes les adresses de ce dépôt sont fictifs et invalides.

## Créer le dépôt du binôme

Le pilote du binôme crée son propre dépôt à partir de ce modèle : bouton **Use this template**, **Create a new repository**, son compte, nom `audit-sync-tarifs`, **Private**. Dans ce dépôt, **Settings**, **Collaborators** : il ajoute son binôme et le formateur. Puis, sur son poste (`<compte>` : le compte GitHub du pilote) :

```bash
git clone https://github.com/<compte>/audit-sync-tarifs
cd audit-sync-tarifs
python3 -m unittest
python3 sync_tarifs.py --fichier data/tarifs_materiaux_riviere.csv
python3 sync_tarifs.py --reference LAINE-R5
```

Sous Windows, remplacez `python3` par `py`. Les options `--url` et `--fiches` contactent des adresses fictives : ne les utilisez pas.

## Fichiers

| Fichier | Rôle |
|---|---|
| `sync_tarifs.py` | Le script à auditer et à corriger |
| `AUDIT.md` | Votre tableau d’audit, à remplir |
| `tests/test_failles.py` | Vos tests de non-régression, à écrire |
| `tests/test_sync.py` | Fichier de la formation : ne pas modifier. Les tests du comportement légitime |
| `data/tarifs_materiaux_riviere.csv` | Fichier de la formation : ne pas modifier. Un fichier fournisseur légitime |
