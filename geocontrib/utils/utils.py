from django.apps import apps
from django.contrib.gis.db.models import Extent

def apply_permissions_to_queryset(user, queryset, project, action="edit", new_status=None):
    """
    Applique les permissions au queryset en fonction du rôle de l'utilisateur et du projet.

    Cette fonction gère deux types d'actions :
    - "edit" : Filtre les signalements que l'utilisateur peut modifier et vérifier s'il peut changer de statut.
    - "delete" : Filtre les signalements que l'utilisateur peut supprimer.

    Args:
        user (User): L'utilisateur effectuant l'action.
        queryset (QuerySet): Le queryset des signalements à filtrer.
        project (Project): Le projet concerné.
        action (str, optional): "edit" ou "delete". Par défaut "edit".
        new_status (str, optional): Statut cible du signalement à modifier.

    Returns:
        QuerySet: Le queryset filtré en fonction des permissions de l'utilisateur.
    """

    # Récupération des modèles nécessaires
    Authorization = apps.get_model(app_label='geocontrib', model_name='Authorization')
    # Un super administrateur a tous les droits
    if user.is_superuser:
        return queryset

    # Vérification du rôle administrateur du projet
    is_project_administrator = Authorization.has_permission(user, 'is_project_administrator', project)

    ## Gestion de l'édition des signalements
    if action == "edit":
        # Vérification du mode de modération
        is_moderated = project.moderation
        # Vérification des autres rôle utilisateur dans le projet nécessaires seulement à l'édition
        is_project_moderator = Authorization.has_permission(user, 'is_project_moderator', project)
        is_project_super_contributor = Authorization.has_permission(user, 'is_project_super_contributor', project)
        is_project_contributor = Authorization.has_permission(user, 'is_project_contributor', project)

        # Définition des statuts modifiables par rôle
        if is_project_administrator or is_project_moderator or (is_project_contributor and not is_moderated):
            # statuts toujours disponibles: Brouillon, Publié, Archivé (sauf en attente à destination des contributeurs et supercontributeurs en projet modéré)
            valid_statuses = ["draft", "published", "archived"]

        elif is_moderated:
            if is_project_super_contributor:
                # Super Contributeur en mode modéré : Peut modifier vers brouillon, en attente
                valid_statuses = ["draft", "pending"]
            elif is_project_contributor:
                # Contributeur peut modifier vers tous les statuts disponibles (ses propres signalements) sauf vers publié dans un projet modéré
                valid_statuses = ["draft", "pending", "archived"] 

        # Sélection des signalements modifiable selon leur statut et le rôle de l'utilisateur
        if is_project_administrator:
            # Administrateur peut modifier tous les statuts
            queryset = queryset.filter(status__in=['draft', 'pending', 'published', 'archived'])
        elif  is_project_moderator or is_project_super_contributor or is_project_contributor:
            # Les autres utilisateurs peuvent modifier tous les statuts sauf archivé
            queryset = queryset.filter(status__in=['draft', 'pending', 'published'])
            if is_project_contributor:
                # Contributeur ne peut modifier que ses propres signalements
                queryset = queryset.filter(creator=user)

        else:
            return queryset.none()  # Aucun accès

        # Vérification du statut cible
        if new_status and new_status not in valid_statuses:
            return queryset.none()

        return queryset

    ## Gestion de la suppression des signalements
    elif action == "delete":
        if is_project_administrator:
            return queryset  # L'admin peut tout supprimer

        else: # un autre utilisateur peut supprimer seulement ses propres signalements
            return queryset.filter(creator=user)

    ## Par défaut, accès interdit
    return queryset.none()


def get_feature_bbox(feature, buffer_m=50, to_string=False):
    """
    Retourne la bbox de la feature avec un buffer précis en mètres.

    Cette fonction :
    - transforme la géométrie dans un SRID métrique (EPSG:3857) pour appliquer
      un buffer en mètres,
    - retransforme la géométrie en EPSG:4326 (lon/lat) pour l'utilisation côté front,
    - retourne la bbox sous forme de dict {'minLon', 'minLat', 'maxLon', 'maxLat'}
      ou en string si `to_string=True`.

    Args:
        feature: instance de Feature possédant un champ `geom`.
        buffer_m: taille du padding en mètres autour de la géométrie.
        to_string: si True, retourne la bbox sous forme de string "minLon,minLat,maxLon,maxLat".

    Returns:
        dict ou str représentant la bbox, ou None si la feature n'a pas de géométrie.
    """
    geom = getattr(feature, "geom", None)
    if not geom:
        return None

    # transformer dans un SRID métrique pour le buffer
    geom_3857 = geom.transform(3857, clone=True)
    buffered = geom_3857.buffer(buffer_m)
    # repasser en lon/lat
    buffered = buffered.transform(4326, clone=True)

    minx, miny, maxx, maxy = buffered.extent
    bbox_dict = {
        "minLon": minx,
        "minLat": miny,
        "maxLon": maxx,
        "maxLat": maxy
    }

    if to_string:
        return f"{minx},{miny},{maxx},{maxy}"
    return bbox_dict
