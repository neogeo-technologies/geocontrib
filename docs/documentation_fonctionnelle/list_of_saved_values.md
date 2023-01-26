# Liste de valeurs pré-enregistrées

La liste de valeurs pré-enregistrées est un type de champ personnalisé qui permet à un administrateur de projet de proposer une liste de valeurs importée via un fichier JSON à ses contributeurs.

Afin de créer une liste de valeurs pré-enregistrée il faut :
* dans l'admin Django, l'administrateur doit se rendre dans la table "Valeurs ré-enregistrées" et cliquer sur le bouton "Ajouter une valeur pré-enregistrée". Il donne alors un nom à sa liste et en renseigne ses options en collant le contenu du fichier JSON ou en y inscrivant les données de son choix. Le forme de la données doit être la suivante : ["data1","data3","data3",...] en ajoutant autant d'options que souhaité.

* A la création du type de signalement, l'administrateur peut sélectionner le type "Liste de valeurs pré-enregistrées" pour un champ personnalisé et il chosit ensuite la liste pré-enregistrée dans l'admin Django qu'il souhaite utiliser.

Lors de la contribution, l'utilisateur pourra alors retrouver ce champ sous-la forme d'une liste déroulante dans laquelle apparaissent les 10 première otpions puis il peut taper dans le champ les premiers caractères de l'option qu'il souhaite retrouver. Les options correspondant à sa recherche lui seront proposées dans la limite de 10.

Ce champ personnalisé peut être utile pour les listes trop longues pour être ajoutées à la main telles que la liste des communes, la liste des bureaux de vote dans un canton, etc. ...

---

[Retour à l'accueil](<index.md>)
