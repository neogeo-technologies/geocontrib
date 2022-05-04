# Tests end-to-end

Les tests end-to-end fournis permettent de vérifier les fonctionnalités principales de l'application GeoContrib. Les numéros des fichiers .robot correspondent aux numéros des chapitres du plan de validation.


## Licence et auteurs

Ces tests sont principalement créés par Neogeo Technologies sous la licence suivante :
Apache License 2.0
http://www.apache.org/licenses/LICENSE-2.0


---


## TABLE DES MATIÈRES
 - [TABLE DES MATIÈRES](#TABLE-DES-MATIÈRES)
 - [Installation](#Installation)
   - [Prérequis](#Prérequis)
   - [Lancement des tests](#Lancement-des-tests)
 - [Configuration](#Configuration)
   - [Variables à éditer dans test_suite.robot](#Variables-à-éditer-dans-test_suite.robot)
- [Fonctionnalités testées](#Fonctionnalités-testées)
    - [Connexion](#Connexion)
    - [Création d'objets](#Création-d'objets)
- [Lancement des tests](#Lancement-des-tests)
- [Méthodologie utilisée](#Méthodologie-utilisée)


---


## Installation

### Prérequis

- Mozilla Firefox avec Geckodriver (https://github.com/mozilla/geckodriver) ou navigateur Chromium avec ChromeDriver (https://chromedriver.chromium.org/downloads)
- Version de GeoContrib fournie

L'utilisation d'un environnement virtuel est recommandée

```shell
# Installation des outils de test et du driver
pip install -r src/docs/end-to-end/requirements.txt
```

Avoir créé un utilisateur ayant le statut de super-utilisateur, par défaut le nom d'utilisateur est 'admin_robot', le mot de passe 'roboto2022?' et le prénom et nom (nom d'affichage) est 'Admin Robot'
Pour des questions de sécurité, l'utilisateur doit à supprimer à la fin des tests (cela n'est pas encore automatisé).

## Configuration

Par défaut, les test sont confiqurés pour tester sur la version locale de geocontrib (localhost:8080), afin de tester les instances en ligne, il est possible de le configurer dans un fichier .env à placer à la racine du projet, s'il n'existe pas déjà.

Copier le contenu du fichier .env_sample/.env dans le fichier .env

### Variables pouvant être éditer dans .env

- GEOCONTRIB_URL
- ADMIN_URL
- SUPERUSERNAME  Utilisateur avec droits d'administration, de super-utilisateur et de gestionnaire équipe
- SUPERUSERPASSWORD
- SUPERUSERDISPLAYNAME


## Fonctionnalités testées

### Connexion

    - avec un compte superuser
    - déconnexion

### Création d'objets

    - projet
    - type de signalement
    - signalement


## Lancement des tests

```shell
robot test_suite.robot
```


## Méthodologie utilisée

- Enregistrement de scenarios de tests avec l'extension Katalon Recorder sur Chromium (documentation disponible sur https://docs.katalon.com/katalon-recorder/docs/overview.html)
- Structure des tests avec RobotFramework (documentation disponible sur https://robotframework.org/)
- Création des bibliothèques en Python
