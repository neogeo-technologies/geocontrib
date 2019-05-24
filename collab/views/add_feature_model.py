from ..actions import create_model
from collab import models as custom
from collab.choices import GEOM_TYPE
from collab.choices import STATUS
from collab.views.project_services import project_features_types
from django.conf import settings
from django.contrib.gis.db import models
from django.db import connection
from django.db.models import Manager as GeoManager
from django.shortcuts import render
from hashlib import md5
import re
import logging

APP_NAME = __package__.split('.')[0]
DEFAULT_FIELDS = ['feature_id', 'creation_date', 'modification_date',
                  'title', 'description', 'geom', 'status',
                  'archive_date', 'deletion_date', 'user', 'project']


def add_feature_model(request):

    if request.method == 'POST':
        if request.POST.get('project') and request.POST.get('feature') and \
           request.POST.get('geom_type'):
            message = generate_feature_model(request.POST.get('project'),
                                             request.POST.get('feature'),
                                             request.POST.get('geom_type'),
                                             request.POST.getlist('field_name' , []),
                                             request.POST.getlist('field_type', []),
                                             request.user)
            context = message
            return render(request, APP_NAME + '/feature/add_feature_model.html',
                          context=context)
        else:
            projects = custom.Project.objects.all()
            context = {'projects': projects, 'error': "Les paramètres obligatoires sont manquants."}
            return render(request, APP_NAME + '/feature/add_feature_model.html',
                          context=context)
    else:
        projects = custom.Project.objects.all()
        context = {'projects': projects}
        return render(request, APP_NAME + '/feature/add_feature_model.html',
                      context=context)


def generate_feature_model(projet_id, feature, geom_type, names, types, user):

    # Get project
    projet = custom.Project.objects.get(id=projet_id)

    # check the fields names given by users
    intersection = list(set(names) & set(DEFAULT_FIELDS))
    if intersection:
        return {'error': """Le(s) champ(s) suivant(s) font déjà partie du modèle de base
            d'un signalement, il n'est pas nécessaire de les recréer: """ +  ','.join(intersection)}
    if len(names) != len(set(names)):
        return {'error': """Veuillez corriger vos champs. Vous avez entré le même nom de champ plusieurs fois."""}
    # check if this feature name does not exist already
    project_features = project_features_types(APP_NAME, projet.slug)
    if feature in project_features:
        return {'error': """Un type de signalement avec ce nom a déjà été créé."""}
    # check title of the feature
    pattern = re.compile("^[a-zA-Z0-9]*$")
    if not pattern.match(feature):
        return {'error': """Le nom du type de signalement ne doit être composé que de chiffres et/ou de lettres (sans accent)."""}

    # geometry model class
    geom_field = models.PointField
    if geom_type == GEOM_TYPE[0][0]:
        print(0)
        geom_field = models.PointField
    elif geom_type == GEOM_TYPE[1][0]:
        print(1)
        geom_field = models.LineStringField
    elif geom_type == GEOM_TYPE[2][0]:
        print(2)
        geom_field = models.PolygonField

    fields = {
        'objects': GeoManager(),
        'feature_id': models.UUIDField(editable=False, max_length=32,
                                       null=True, blank=True),
        'creation_date': models.DateTimeField("Date de l'évènement",
                                              auto_now_add=True,
                                              null=True, blank=True),
        'modification_date': models.DateTimeField("Date de maj",
                                                  auto_now=True,
                                                  null=True, blank=True),
        'title': models.CharField('Titre', max_length=128, null=True,
                                  blank=True),
        'description': models.TextField('Description', blank=True, null=True),
        'geom': geom_field(null=False, srid=settings.DB_SRID, dim=2),
        'status': models.CharField('Statut des signalements',
                                   choices=STATUS,
                                   max_length=1, default='0',
                                   null=True, blank=True),
        'archive_date': models.DateField("Date d'archivage automatique",
                                           null=True, blank=True),
        'deletion_date': models.DateField("Date de suppression automatique",
                                             null=True, blank=True),
        'user': models.ForeignKey(custom.CustomUser, related_name='models',
                                  on_delete=models.PROTECT,
                                  help_text="Utilisateur abonné"),
        'project': models.ForeignKey(custom.Project, related_name='models',
                                    on_delete=models.PROTECT,
                                    help_text="Projet"),
        '__str__': lambda self: '%s %s' (self.title),
        }

    labels = {"creation_date": "Date de création",
              "modification_date": "Date de le dernière mise à jour",
              "title": "Titre",
              "description": "Description",
              "geom": "Geométrie",
              "status": "Statut des signalements",
              "archive_date": "Date d'archivage automatique",
              "deletion_date": "Date de suppression automatique"}

    module = 'config.' + APP_NAME
    field_type = []
    for elt in range(0, len(types)):
        if names[elt] and types[elt]:
            if types[elt] == 'string':
                field_type.append(models.CharField(max_length=255, blank=True))
            elif types[elt] == 'date':
                field_type.append(models.DateTimeField(blank=True, null=True))
            elif types[elt] == 'int':
                field_type.append(models.IntegerField(blank=True, null=True))
            elif types[elt] == 'float':
                field_type.append(models.FloatField(blank=True, null=True))
            elif types[elt] == 'boolean':
                field_type.append(models.BooleanField(blank=True, null=True))
            elif types[elt] == 'text':
                field_type.append(models.TextField(max_length=255,
                                                   blank=True, null=True))
            fields[names[elt]] = field_type[elt]
            labels[names[elt]] = names[elt]

    # creation modele
    model = create_model(projet.slug + '_' + feature, fields,
                         app_label=APP_NAME,
                         module=module,
                         admin_opts={})

    try:
        with connection.schema_editor() as editor:
            editor.create_model(model)

        # ajout du nom de la table
        table_name = APP_NAME + "_" + projet.slug + '_' + feature
        if not projet.features_info:
            projet.features_info = {feature: {'table_name': table_name,
                                              'geom_type': GEOM_TYPE[int(geom_type)][1],
                                              'feature': feature,
                                              'user_id': user.id,
                                              'labels': labels}}
        else:
            projet.features_info.update({feature: {
                                        'table_name': table_name,
                                        'geom_type': GEOM_TYPE[int(geom_type)][1],
                                        'feature': feature,
                                        'user_id': user.id,
                                        'labels': labels}})
        projet.save()
        return {'success': "Le type de signalement a été créé avec succès."}
    except Exception as e:
        msg = "Une erreur s'est produite, veuillez renouveller votre demande ultérieurement"
        logger = logging.getLogger(__name__)
        logger.exception(msg)
        return {'error': msg}
