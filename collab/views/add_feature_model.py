import uuid
from collab import models as custom
from collab.choices import GEOM_TYPE
from collab.choices import STATUS
from collab.models import FeatureType
from collab.views.services.project_services import project_features_types
from collab.views.views import get_anonymous_rights
from django.conf import settings
from django.contrib import admin
from django.contrib.gis.db import models
from django.db import connection
from django.db.models import Manager as GeoManager
from django.shortcuts import render
from django.utils.text import slugify
from hashlib import md5
import re
import logging

APP_NAME = __package__.split('.')[0]
DEFAULT_FIELDS = ['feature_id', 'creation_date', 'modification_date',
                  'title', 'description', 'geom', 'status',
                  'archive_date', 'deletion_date', 'user', 'project']


def create_model(name, fields=None, app_label='', module='', options=None, admin_opts=None):
    """
    Create specified model
    """
    class Meta:
        # Using type('Meta', ...) gives a dictproxy error during model creation
        pass

    if app_label:
        # app_label must be set using the Meta inner class
        setattr(Meta, 'app_label', app_label)

    # Update Meta with any options that were provided
    if options is not None:

        for key, value in options.iteritems():
            setattr(Meta, key, value)

    # Set up a dictionary to simulate declarations within a class
    attrs = {'__module__': module, 'Meta': Meta}

    # Add in any fields that were provided
    if fields:
        attrs.update(fields)

    # Create the class, which automatically triggers ModelBase processing
    model = type(name, (models.Model,), attrs)

    # Create an Admin class if admin options were provided
    if admin_opts is not None:
        class Admin(admin.ModelAdmin):
            pass
        for key, value in admin_opts:
            setattr(Admin, key, value)
        admin.site.register(model, Admin)

    return model


def add_feature_model(request, project_slug):

    try:
        project = custom.Project.objects.get(slug=project_slug)
    except Exception as e:
        context = {"error": "Le projest est introuvable"}
        return render(request, APP_NAME + '/feature/add_feature_model.html',
                      context=context)
    # get user right on project
    if not request.user.is_authenticated:
        rights = get_anonymous_rights(project)
        context = {"rights": rights}
        return render(request, APP_NAME + '/feature/add_feature_model.html',
                      context=context)
    else:
        rights = request.user.project_right(project)

    if request.method == 'POST':
        if project and request.POST.get('feature') and \
           request.POST.get('geom_type'):
            message = generate_feature_model(project,
                                             request.POST.get('feature'),
                                             request.POST.get('geom_type'),
                                             request.POST.getlist('field_name' , []),
                                             request.POST.getlist('field_type', []),
                                             request.POST.getlist('labels' , []),
                                             request.user)
            context = {'project': project, 'rights': rights}
            if message.get('error', ''):
                context['error'] = message.get('error', '')
            if message.get('success', ''):
                context['success'] = message.get('success', '')
            return render(request, APP_NAME + '/feature/add_feature_model.html',
                          context=context)
        else:
            context = {'project': project, 'rights': rights, 'error': "Les paramètres obligatoires sont manquants."}
            return render(request, APP_NAME + '/feature/add_feature_model.html',
                          context=context)
    else:
        context = {'project': project, 'rights': rights}
        return render(request, APP_NAME + '/feature/add_feature_model.html',
                      context=context)


def generate_feature_model(project, feature, geom_type, names, types, labels, user):

    # check the fields names given by users
    intersection = list(set(names) & set(DEFAULT_FIELDS))
    if intersection:
        return {'error': """Le(s) champ(s) suivant(s) font déjà partie du modèle de base
            d'un signalement, il n'est pas nécessaire de les recréer: """ +  ','.join(intersection)}
    if len(names) != len(set(names)):
        return {'error': """Veuillez corriger vos champs. Vous avez entré le même nom de champ plusieurs fois."""}
    # check if this feature name does not exist already
    feature_slug = slugify(feature)
    project_features = project_features_types(APP_NAME, project.slug)
    if feature_slug in project_features:
        return {'error': """Un type de signalement avec ce nom a déjà été créé."""}
    # check title of the feature
    pattern = re.compile("^[a-zA-Z0-9]*$")
    if not pattern.match(feature_slug):
        return {'error': """Le nom du type de signalement ne doit être composé que de chiffres et/ou de lettres (sans accent)."""}
    # geometry model class
    geom_field = models.PointField
    if geom_type == GEOM_TYPE[0][0]:
        geom_field = models.PointField
    elif geom_type == GEOM_TYPE[1][0]:
        geom_field = models.LineStringField
    elif geom_type == GEOM_TYPE[2][0]:
        geom_field = models.PolygonField

    fields = {
        'objects': GeoManager(),
        'feature_id': models.UUIDField(primary_key=True, editable=False,
                                       default=uuid.uuid4, null=True),
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

    dict_labels = {"creation_date": "Date de création",
                   "modification_date": "Date de la dernière mise à jour",
                   "title": "Titre",
                   "description": "Description",
                   "geom": "Géométrie",
                   "status": "Statut des signalements",
                   "archive_date": "Date d'archivage automatique",
                   "deletion_date": "Date de suppression automatique"}


    module = 'config.' + APP_NAME
    field_type = []
    for elt in range(0, len(types)):
        if names[elt] and types[elt]:
            if types[elt] == 'string':
                field_type.append(models.CharField(max_length=255, blank=True, null=True))
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
            dict_labels.update({names[elt]: labels[elt]})
            # dict_labels[names[elt]] = labels[elt]
    # creation modele
    model = create_model(project.slug + '_' + feature_slug, fields,
                         app_label=APP_NAME,
                         module=module,
                         admin_opts={})

    try:
        with connection.schema_editor() as editor:
            editor.create_model(model)

        FeatureType.objects.create(name=feature, user=user,
                                   project=project,
                                   geom_type=geom_type,
                                   feature_type_slug=feature_slug,
                                   wording=dict_labels)

        project.save()
        # create new feature type
        custom.Event.objects.create(
            user=user,
            event_type='create',
            object_type='feature',
            project_slug=project.slug,
            feature_type_slug=feature_slug,
        )

        return {'success': "Le type de signalement a été créé avec succès."}

    except Exception as e:
        msg = "Une erreur s'est produite, veuillez renouveller votre demande ultérieurement"
        logger = logging.getLogger(__name__)
        logger.exception(msg)
        return {'error': msg}
