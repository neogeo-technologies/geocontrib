# Collab

Application de signalement collaboratif

# Déploiement pour dev

## Création projet Django et clone du repo
```shell
python3.5 -m venv collab_venv/
source collab_venv/bin/activate
git clone git@github.com:neogeo-technologies/collab.git src/
# Installer les dépendances
django-admin startproject config .

# Ajout de liens symboliques pour que les sources git soient visible par Django
ln -s src/collab/ .
ln -s src/api/ .
```

## Settings & URL's

Édition du fichier de configuration et du fichier d'url.

## Migrations et ajout de données initiales

```shell
python manage.py migrate
python manage.py loaddata src/collab/data/perm.json
```

## Définir une image par défaut.
Fichier à copier dans dossier de stockage des média, défini dans les settings
```
cp src/collab/static/collab/img/default.png media/
cp src/collab/static/collab/img/logo.png media/
```

## Définir le domaine et le nom du site.

Ces données sont à définir depuis l'admin Django dans la section Site et
permettent notamment d'afficher les url dans les gabarit d'e-mail

## Dump et load de la base de recette sans conflits.

```
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 4 > dump.json
```

# TODO:

- [x] Import en masse
- [x] Import de photographie
- [x] Téléchargement
- [ ] Abonnement
- [x] Projet: Changer niveau d'autorisation
- [x] Projet: Administrer les membres: cf service api GET projects/<slug:slug>/utilisateurs
- [ ] Feature: Liaison entre Features
- [x] Feature: Affichage et edition carto
- [x] Mon Profil: Template à revoir
- [x] Permissions: Administrateur de projet ajout et màj
- [x] Commentaire
- [x] Filtrer les signalements selon autorisation de l'utilisateur
