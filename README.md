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

Édition du fichier de configuration et du fichier d'url

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

# TODO:
- [ ] Import en masse
- [ ] Import de photographie
- [ ] Téléchargement
- [ ] Abonnement
- [ ] Projet: Changer niveau d'autorisation
- [ ] Projet: Administrer les membres: cf service api GET projects/<slug:slug>/utilisateurs
- [x] Feature: Liaison entre Features
- [ ] Feature: Affichage et edition carto
- [ ] Mon Profil: Template à revoir
- [x] Permissions: User.is_administrator: Authorization.is_project_administrator/give_adminstration_perms
- [ ] Commentaire
- [x] Filtrer les signalements selon autorisation de l'utilisateur


# Informations permissions utilisateur

Qui peut créer un projet?
  - user.is_administrator == True

Qui peut créer une feature ?
  - Authorization.has_permission(user, 'can_create_feature', project)
    - équivalent à user_rank >= CONTRIBUTOR

Qui peut modifier une feature ?
  - Authorization.has_permission(user, 'can_update_feature', project, feature)
    - équivalent à user_rank >= MODERATOR OR user == feature.user

Qui peut publier une feature si projet modéré?
  - Authorization.has_permission(user, 'can_publish_feature', project, feature)
    - équivalent à user_rank >= MODERATOR
