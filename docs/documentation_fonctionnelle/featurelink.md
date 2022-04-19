# Liaisons entre signalements

Il est possible de créer trois types de liaisons entre un signalement A et un signalement B :
* **"doublon"**
* **"dépend de"**
* **"remplace"**

Pour chaque liaison, un adjectif inverse est défini :
* Si la liaison "doublon de B" est affectée à A, la liaison "doublon de A" est affectée à B.
* Si la liaison "dépend de B" est affectée à A, la liaison "dépend de A" est affectée à B.
* Si la liaison "remplace B" est affectée à A, la liaison "est remplacé par A" est affectée à B.

## Ajout d'une liaison

Pour ajouter une liaison depuis le formulaire d'édition d'un signalement, il faut cliquer sur le bouton _"Ajouter une liaison"_ dans la rubrique _"Signalements liés"_, et sélectionner un autre signalement appartenant au même type de signalement.

## Ajout d'une liaison de type doublon suite à un import

Suite à un import de données par upload d'un fichier GeoJSON, si deux signalements d'un même type de signalements présentent le même titre et la même géométrie, ils sont alors automatiquement considérés comme "doublons". La liaison est alors visible dans chacune des pages descriptives de ces signalements.

## Depuis l'interface d'administration de Django

Dans l'interface d'administration, les super-utilisateurs peuvent rechercher, publier, supprimer et archiver des signalements liés sous le menu _"Liaisons entre signalements"_.

---

[Retour à l'accueil](<index.md>)
