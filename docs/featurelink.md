# Liaisons entre signalements

Il est possible de créer trois types de liaisons entre un signalement A et un signalement B :
* "doublon"
* "dépend de"
* "remplace"

Pour chaque liaison, un adjectif inverse est défini :
* Si la liaison "doublon de B" est affectée à A, la liaison "doublon de A" est affectée à B.
* Si la liaison "dépend de B" est affectée à A, la liaison "dépend de A" est affectée à B.
* Si la liaison "remplace B" est affectée à A, la liaison "est remplacé par A" est affectée à B.

## Création

Pour ajouter une liaison, il faut, lors de la création d'un signalement, cliquer sur "Ajouter une liaison" sous "Signalements liés", et sélectionner un autre signalement appartenant au même type de signalement.

## Depuis l'interface d'administration de Django

Dans l'interface d'administration, il est possible de rechercher, publier, supprimer et archiver des signalements liés sous le menu "Liaisons entre signalements".
