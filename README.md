# Collab

Application de signalement collaboratif

# Déploiement pour dev

```shell
python3.5 -m venv collab_venv/
source bin/activate
git clone git@github.com:neogeo-technologies/collab.git src/
pip install -r src/requirements.txt
django-admin startproject config .

# Ajout de liens symboliques pour que les sources git soient visible par Django
ln -s src/collab/ .
ln -s src/api/ .
```

# Conf
Edit config/settings.py config/urls.py CF config_sample/*


# Migrations et ajout de données initiales

```shell
python manage.py migrate
python manage.py loaddata src/collab/data/perm.json
```

# Définir une image par défaut.
Fichier à copier dans dossier de stockage des média, défini dans les settings
```
cp src/collab/static/collab/img/default.png media/
```

# TODO:
- [ ] Import en masse
- [ ] Import de photographie
- [ ] Telechargement
- [ ] Abonnement
- [ ] Projet: Changer niveau d'authenticité
- [x] Projet: Administrer les membres
- [ ] Feature: Liaison entre Features
- [ ] Feature: Affichage et edition carto
- [ ] Mon Profil: Template à revoir
- [ ] Permissions: User.is_administrator: Authorization.is_project_administrator/give_adminstration_perms
