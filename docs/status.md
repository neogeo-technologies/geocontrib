# Statuts et cycle de vie des signalements

Brouillon :
* ce statut permet à son auteur de commencer à saisir un signalement et de le sauvegarder afin de le finaliser plus 
tard (lorsqu'il aura récolté des informations complémentaires par exemple)
* statut du signalement à sa création
* peut être rebasculé dans ce statut par son auteur, un modérateur ou un administrateur du projet
* seuls l'auteur du signalement et les super utilisateurs Django peuvent consulter un signalement avec ce statut et 
réaliser des actions sur un signalement avec ce statut

En attente de publication :
* ce statut n’existe pas pour un projet sans modération
* peut être basculé dans ce statut par son auteur ou un administrateur
* seuls l'auteur du signalement, les modérateurs du projet, les administrateurs du projet et les super-utilisateurs 
Django peuvent consulter un signalement avec ce statut

Publié :
* peut être basculé dans ce statut par un modérateur ou un administrateur du projet
* peut être rebasculé dans ce statut par son auteur uniquement lorsque le projet est sans modération
* l'utilisateur courant peut avoir accès à un signalement publié si son niveau d'autorisation est au moins aussi haut 
que le paramètre du projet "Visibilité des signalements publiés"

Archivé :
* peut être basculé dans ce statut par son auteur, un modérateur ou un administrateur du projet (uniquement à partir 
de l’état publié)
* est également basculé dans ce statut de manière automatique par l’outil lui-même lorsque la date d’archivage 
automatique est dépassée
* l'utilisateur courant peut avoir accès à un signalement publié si son niveau d'autorisation est au moins aussi haut 
que le paramètre du projet "Visibilité des signalements archivés"