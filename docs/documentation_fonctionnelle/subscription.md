# Abonnements

## Abonnement à un projet

Pour chacun des projets, les utilisateurs possédant un compte dans l'application, et authentifiés, peuvent s'abonner aux activités des projets qu'ils ont le droit de visiter depuis leur page d'accueil, grâce au bouton _S'abonner au projet_ .

Au clic sur le bouton, une popup s'ouvre et propose à l'utilisateur de s'abonner au projet. S'il clique une seconde fois, la popup propose cette fois le désabonnement.

Lorsqu'un utilisateur est abonné au projet, il sera notifié par email de l'activité du projet c'est à dire des nouvelles publications, nouveaux commentaires, modifications, etc.

La périodicité des emails dépend de la configuration utilisée à l'installation de l'application. Elle n'est pas modulable pour chacun des projets.

## Gestion des abonnements dans le BO Django

Dès lors qu'un utilisateur s'abonne a un projet, un `objet abonnement` (Subscription object) est ajouté dans la table des abonnements visible depuis Django, correspondant à la liste d'abonnées pour ce projet.

Pour chaque projet, il est possible de sélectionner / désélectionner les utilisateurs qui doivent bénéficier de l'abonnement au projet en éditant l'objet Abonnement correspondant.

Pour désabonner tous les utilisateurs d'un projet, il suffit de supprimer l'objet Abonnement.

---

[Retour à l'accueil](<index.md>)
