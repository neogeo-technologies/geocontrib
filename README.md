![alt text](geocontrib/static/geocontrib/img/logo-geocontrib.png?raw=true)

GéoContrib est un outil libre de signalement contributif et collaboratif. Une version de démonstration est accessible sur https://geocontrib.demo.neogeo.fr/.

## Installation

### Prérequis

* Python 3.7 (minimum 3.6)
* Instance de PostgreSQL/PostGIS avec une base de données dédiée à l'application 
(cf. paramètre DATABASES du fichier settings.py)

### Création du projet Django et clone du repo

```shell
# Création d'un environnement virtuel Python
python3 -m venv geocontrib_venv/

# Activation de cet environnement
source geocontrib_venv/bin/activate

# Clonage du projet - récupération des sources
# Actuellement, la branche par défaut du projet est develop
# Ce sera celle qui sera active par défaut immédiatement après le clonage
git clone https://github.com/neogeo-technologies/geocontrib.git
cd geocontrib

# Installer les dépendances
pip install -r requirements.txt

# Création d'un projet Django
django-admin startproject config .
```

### Édition des fichiers settings.py et url.py

Copier le contenu du fichier config_sample/settings.py dans /config/settings.py.

Éditer les paramètres classiques de Django dans /config/settings.py :
* SECRET_KEY https://docs.djangoproject.com/en/2.2/ref/settings/#secret-key
* DEBUG https://docs.djangoproject.com/en/2.2/ref/settings/#debug
* DATABASES https://docs.djangoproject.com/en/2.2/ref/settings/#databases
* TIME_ZONE https://docs.djangoproject.com/en/2.2/ref/settings/#std%3Asetting-TIME_ZONE
* STATIC_ROOT https://docs.djangoproject.com/en/2.2/ref/settings/#static-root
* MEDIA_ROOT https://docs.djangoproject.com/en/2.2/ref/settings/#media-root
* LOGGING https://docs.djangoproject.com/en/2.2/ref/settings/#logging
* EMAIL_HOST https://docs.djangoproject.com/en/2.2/ref/settings/#email-host
* EMAIL_PORT https://docs.djangoproject.com/en/2.2/ref/settings/#email-port
* EMAIL_USE_TLS https://docs.djangoproject.com/en/2.2/ref/settings/#email-use-tls
* EMAIL_HOST_USER https://docs.djangoproject.com/en/2.2/ref/settings/#std%3Asetting-EMAIL_HOST_USER
* EMAIL_HOST_PASSWORD https://docs.djangoproject.com/en/2.2/ref/settings/#email-host-password
* DEFAULT_FROM_EMAIL https://docs.djangoproject.com/en/2.2/ref/settings/#default-from-email
* DATA_UPLOAD_MAX_NUMBER_FIELDS https://docs.djangoproject.com/fr/2.2/ref/settings/#data-upload-max-number-fields
* LOGIN_URL https://docs.djangoproject.com/fr/3.1/ref/settings/#login-url

Éditer les paramètres spécifiques à l'outil dans /config/settings.py :
* BASE_URL : URL du site, par exemple "https://geocontrib.deme.neogeo.fr"
* DEFAULT_SENDING_FREQUENCY : fréquence d'envoi des notifications par email (never/instantly/daily/weekly)
* APPLICATION_NAME : nom de l'application telle qu'elle apparaît dans l'IHM
* APPLICATION_ABSTRACT : description de l'application en langage naturel
* IMAGE_FORMAT : formats autorisés des fichiers téléversés dans l'application
* FILE_MAX_SIZE : taille maximale des fichiers téléversés dans l'application
* DEFAULT_BASE_MAP : configuration du fond de carte par défaut
* PROJECT_COPY_RELATED : configuration des modèles de projets

Copier le contenu du fichier config_sample/urls.py dans config/urls.py

### Création des tables et ajout de données initiales dans la base de données

```shell
python manage.py migrate
python manage.py loaddata geocontrib/data/perm.json
python manage.py loaddata geocontrib/data/flatpages.json
```

Ne faites pas attention aux messages d'avertissement suivants :
```
Sites not migrated yet. Please make sure you have Sites setup on Django Admin
```

### Dépot des images par défaut

Copier l'image par défaut et le logo de l'application dans le répertoire défini par le paramètre MEDIA_ROOT 
du fichier settings.py.

Par exemple, copier les images fournies dans les sources de l'application :
```shell
mkdir media
cp geocontrib/static/geocontrib/img/default.png media/
cp geocontrib/static/geocontrib/img/logo.png media/
cp geocontrib/static/geocontrib/img/logo-neogeo*.png media/
```

### Création d'un superutilisateur

Lancer la commande Django de création d'un super utilisateur et suivre les instructions :
```shell
python manage.py createsuperuser
```

### Paramétrage du domaine et du nom du site

Ces données sont à définir depuis l'admin Django dans la section Site et
permettent notamment d'afficher les url dans les gabarit d'e-mail.
Pour cela, lancer l'application Django :
```shell
python manage.py runserver
```

Se rendre dans l'interface d'administration Django et éditer le premier enregistrement des entités 
"Sites" (cf. yoururl.net/admin/sites/).

## Configuration des tâches périodiques

Deux types de tâches requièrent d'invoquer une commande régulièrement (depuis un cron par exemple)

L'envoi de mails de norifications, vous pouvez l'appeler toutes les minutes ou tous les jours selon vos préférences d'envoi
```shell
python manage.py notify_subscribers
```

L'archivage et la suppression des signalements, à invoquer une fois par jour
```shell
python manage.py data_cleansing
```


## Déploiement dans un environnement geOrchestra

Reportez-vous au README.md présent dans le répertoire `plugin_georchestra`.


## Sauvegarde des données

```
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 4 > dump.json
```

## Génération du graphique du modèle

Après avoir installé graphiz et django-extensions

```
./manage.py graph_models --pygraphviz geocontrib --output docs/model.png
````

Le graphique est disponible ici ![docs/model.png](docs/model.png)
