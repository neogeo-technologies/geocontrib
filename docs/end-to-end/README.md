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
    - [En cours de développement : GeoJson](#En-cours-de-développement-:-GeoJson)
- [Lancement des tests](#Lancement-des-tests)
- [Méthodologie utilisée](#Méthodologie-utilisée)


---


## Installation

### Prérequis

GeoContrib
geocontrib_venv activé

```shell
# Installation des outils de test
pip install -r src/docs/end-to-end/requirements.txt
```

## Configuration

### Variables à éditer dans test_suite.robot

- ${URL}
- ${SUPERUSERNAME} : attention, dans cette version, l'utilisateur doit avoir les droits d'administration
- ${SUPERUSERPASSWORD} 


## Fonctionnalités testées

### Connexion
    - avec un compte superuser
    - déconnexion

### Création d'objets
    - projet
    - type de signalement
    - signalement

### En cours de développement : GeoJson
    - import
    - export


## Lancement des tests

```shell
robot test_suite.robot
```


## Méthodologie utilisée

- Scenarios de tests avec Katalon
- Écriture et révision des tests avec RobotFramework
- Création des bibliothèques Python utilisées dans les tests RobotFramework
    