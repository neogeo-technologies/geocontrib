# Collab

Application de signalement collaboratif

# Déploiement pour dev

```shell
python3.5 -m venv /collab_venv
source bin/activate
git clone git@github.com:neogeo-technologies/ng_collab.git .
pip install -r requirements.txt
django-admin startproject config .
```

# Conf
Edit config/settings.py config/urls.py CF config_sample/*


# Migrations et ajout de données initiales

```shell
python manage.py migrate
python manage.py laoddata collab/data/perm.json
```

# Définir une image par défaut.
Fichier à copier dans dossier de stockage des média, défni dans les settings
```
cp collab/static/collab/img/default.png /media
```

# TODO:
- [ ] Import en masse
- [ ] Import de photographie
- [ ] Telechargement
- [ ] Abonnement
- [ ] Projet: Changer niveau d'authenticité
- [ ] Projet: Administrer les membres
- [ ] Feature: Liaison entre Features
- [ ] Feature: Affichage et edition carto
- [ ] Mon Profil: Template à revoir
- [ ] Permissions: User.is_administrator: Authorization.is_project_administrator/give_adminstration_perms
