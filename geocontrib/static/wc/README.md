# Project Preview Web Component

Ce projet fournit un Web Component simple qui permet d'afficher un aperçu de projet d'une instance Geocontrib, incluant une image, un titre et une description. Le composant est conçu pour être facilement intégré sur n'importe quel site web, tel que WordPress ou Drupal, en ajoutant simplement une balise HTML.  

## Fonctionnalités
- Affiche une image, un titre et une description.
- Supporte les appels API pour récupérer dynamiquement les informations du projet.
- Configuration du domaine et slug projet
- Personnalisation des styles par des attributs.

## Installation

### Prérequis
Vous pouvez utiliser ce composant en l'intégrant dans une page web et en pointant vers le script hébergé dans ce dossier.

### Hébergement des sources
Seul le fichier JavaScript est nécessaire pour charger le web component.
Ce fichier est hébergé sur la plateforme Geocontrib concernée.
Il avait été envisagé d'utiliser notre instance GitLab, mais celle-ci ne permet pas de servir des fichiers JavaScript chargés directement depuis du HTML.
Héberger le fichier JavaScript avec l'application Geocontrib garantit qu'il restera disponible tant que l'application est en ligne.

## Utilisation

### Inclusion dans une page HTML
Pour intégrer ce composant sur votre site, ajoutez le code suivant dans votre fichier HTML en ajustant le src du script, le domaine et le slug projet selon votre configuration :

```html
  <!-- Pour modifier la police, ajoutez l'attribut "font" avec le nom de la police souhaitée (par exemple: font="'Roboto Condensed', Lato, 'Helvetica Neue'"). -->
  <!-- Dans le cas où la police souhaitée ne serait pas déjà disponible dans la page affichant le web component, incluez également une balise <style> pour l'importer. -->
  <style>@import url('https://fonts.googleapis.com/css?family=Roboto Condensed:400,700,400italic,700italic&subset=latin');</style>
  <script src="./project-preview.js"></script>
      
  <project-preview
    domain="http://localhost:8000"
    project-slug="1-projet-test"
    width=""
    color=""
    font=""
  ></project-preview>
```
L’interface Geocontrib permet de récupérer ce code via un bouton disponible en haut de la page de détail du projet.
Le code copié contiendra les paramètres déjà configurés selon la plateforme Geocontrib d'où il a été copié.

## Développement et Test Local

Pour tester et développer sur ce web component, un fichier package.json permet de lancer le projet en deux commandes.

Tout d'abord installer les dépendances pour installer le serveur local si ce n'est pas déjà fait, avec:
```shell
npm install
```
Puis démarrer le serveur à l'aide de :
```shell
npm run serve
```
Cela ouvrira le fichier index-wc-demo.html dans le navigateur avec des exemples pré-configurés, n'hésitez pas à les mettre à jour si les projets ou domaines ne sont plus d'actualités et/ou copier un exemple depuis le front