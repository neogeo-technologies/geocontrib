# Statuts et cycle de vie des signalements

**Brouillon**
* Ce statut permet à son auteur de commencer à saisir un signalement et de le sauvegarder afin de le finaliser plus tard (lorsqu'il aura récolté des informations complémentaires par exemple) ;
* Statut du signalement à sa création ;
* Un signalement peut être rebasculé dans ce statut par son auteur, un super-contributeur, un modérateur ou un administrateur du projet ;
* Seul l'auteur du signalement, les supercontributeurs et les super-utilisateurs Django peuvent consulter un signalement avec ce statut, et réaliser des actions sur un signalement avec ce statut.

**En attente de publication**
* Ce statut n’existe pas pour un projet sans modération ;
* Un signalement peut être basculé dans ce statut par son auteur, un supercontribueur ou un administrateur ;
* L'auteur du signalement, les supercontributeurs, les modérateurs du projet, les administrateurs du projet et les super-utilisateurs Django peuvent consulter un signalement avec ce statut.

**Publié**
* Dans le cas de projet modéré, un signalement peut être basculé dans ce statut par un modérateur ou un administrateur du projet ;
* Dans le cas d'un projet non modéré, un signalement peut être basculé dans ce statut par son auteur, un supercontributeur ou un administrateur ;
* L'utilisateur courant peut avoir accès à un signalement publié si son niveau d'autorisation est au moins aussi haut que le paramètre du projet _"Visibilité des signalements publiés"_.

**Archivé**
* Un signalement peut être basculé dans ce statut par son auteur, un modérateur ou un administrateur du projet (uniquement à partir de l’état publié) ;
* Un signalement peut être également basculé dans ce statut de manière automatique par l’outil lui-même lorsque la date d’archivage automatique est dépassée
* L'utilisateur courant peut avoir accès à un signalement archivé si son niveau d'autorisation est au moins aussi haut que le paramètre du projet _"Visibilité des signalements archivés"_.

---

[Retour à l'accueil](<README.md>)
