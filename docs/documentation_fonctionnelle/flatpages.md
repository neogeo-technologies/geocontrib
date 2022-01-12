# Pages statiques

Le module "flatpages" de Django est activé dans GeoContrib pour permettre à des administrateurs de personnaliser les pages statiques de l'outil :
* page _"Aide"_
* page _"Mentions légales"_

L'administration de ces pages est accessible dans l'interface d'administration de Django : _"[url de GéoContrib]/admin/flatpages/flatpage/"_

Dans l'interface d'administration de chacune de ces pages, les administrateurs de l'outil peuvent modifier le contenu de ces pages. Ce contenu doit être du code HTML composé d'éléments `<h2>`, `<h3>`, `<p>` et autres éléments textuels habituels.

Dans la partie avancée du formulaire, il est possible d'indiquer le nom d'un modèle de page à appliquer à la page (champ intitulé ""). Ce champ peut prendre deux valeurs :
* flatpages/default.html (valeur par défaut) : modèle de page simple. Ce modèle est à privilégier pour les pages dont le contenu est court.
* flatpages/with_right_menu.html : modèle de page avec une table des matières à droite qui référence les entrées `<h2>` de la page pour accès rapide. Ce modèle est à privilégier pour les pages avec un contenu long. La table des matières disparaît pour les petits écrans.

**Note :**
* Ne supprimez pas les pages statiques (_"Aide"_ et _"Mentions légales"_). Le pied de page de l'outil est défini dans le code de l'outil. Il ne s'adapte pas dynamiquement à leur absence.
* Ajouter une nouvelle page statique dans l'interface d'administration ne la rendra pas visible dans les menus de l'outil. Le contenu de ces menus est défini dans le code de l'outil. Il ne s'adapte pas dynamiquement en fonction de l'existence ou non de pages statiques supplémentaires.

---

[Retour à l'accueil](<README.md>)
