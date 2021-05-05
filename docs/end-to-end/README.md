# Tests end-to-end

Les tests end-to-end fournis permettent de vérifier les fonctionnalités principales de l'application GeoContrib.


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

Mozilla Firefox 88.0
GeoContrib 1.2 ou 1.3

L'utilisation d'un environnement virtuel est recommandée

```shell
# Installation des outils de test et du driver
pip install -r src/docs/end-to-end/requirements.txt
```

## Configuration

### Variables à éditer dans test_suite.robot

- ${URL}
- ${SUPERUSERNAME}  Utilisateur avec droits d'administration, de super-utilisateur et de gestionnaire équipe
- ${SUPERUSERPASSWORD} 


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
