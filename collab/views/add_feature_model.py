from ..actions import create_model
from collab import models as custom
from collab.choices import STATUS
from collab.views.project_services import project_features_types
from django.contrib.gis.db import models
from django.db import connection
from django.db.models import Manager as GeoManager
from django.shortcuts import render
from hashlib import md5
import re

APP_NAME = __package__.split('.')[0]
DEFAULT_FIELDS = ['feature_id', 'date_creation', 'date_modification',
                  'titre', 'description', 'geometrie', 'status',
                  'date_archivage', 'user', 'project']


def add_feature_model(request):

    if request.method == 'POST':
        if request.POST.get('project') and request.POST.get('feature'):
            message = generate_feature_model(request.POST.get('project'),
                                             request.POST.get('feature'),
                                             request.POST.getlist('field_name' , []),
                                             request.POST.getlist('field_type', []),
                                             request.user)
            context = message
            return render(request, APP_NAME + '/add_feature_model.html',
                          context=context)
        else:
            projects = custom.Project.objects.all()
            context = {'projects': projects, 'error': "Les paramètres obligatoires sont manquants"}
            return render(request, APP_NAME + '/add_feature_model.html',
                          context=context)
    else:
        projects = custom.Project.objects.all()
        context = {'projects': projects}
        return render(request, APP_NAME + '/add_feature_model.html',
                      context=context)


def generate_feature_model(projet_id, feature, names, types, user):

    # Get project
    projet = custom.Project.objects.get(id=projet_id)
    # check the fields names given by users
    intersection = list(set(names) & set(DEFAULT_FIELDS))
    if intersection:
        return {'error': """Le(s) champ(s) suivant(s) font déjà parti du modèle de base
            d'un signalement, il n'est pas nécessaire de les recréer: """ +  ','.join(intersection)}
    if len(names) != len(set(names)):
        return {'error': """Veuillez corriger vos champs. Vous avez entré le même nom de champ plusieurs fois"""}
    # check if this feature name does not exist already
    project_features = project_features_types(APP_NAME, projet.slug)
    if feature in project_features:
        return {'error': """Un signalement avec ce nom a déjà étè crée"""}
    # check title of the feature
    pattern = re.compile("^[a-zA-Z0-9]*$")
    if not pattern.match(feature):
        return {'error': """Le nom du signalement ne doit être composé que de chiffres et/ou de lettres (sans accent)"""}

    fields = {
        'objects': GeoManager(),
        'feature_id': models.UUIDField(editable=False, max_length=32,
                                       null=True, blank=True),
        'date_creation': models.DateTimeField("Date de l'évènement",
                                              auto_now_add=True,
                                              null=True, blank=True),
        'date_modification': models.DateTimeField("Date de maj",
                                                  auto_now=True,
                                                  null=True, blank=True),
        'titre': models.CharField('Titre', max_length=128, null=True,
                                  blank=True),
        'description': models.TextField('Description', blank=True, null=True),
        'geometrie': models.GeometryField(null=True, blank=True),
        'status': models.CharField('Status des signalements',
                                   choices=STATUS,
                                   max_length=1, default='0',
                                   null=True, blank=True),
        'date_archivage': models.DateField("Date d'archivage automatique",
                                           null=True, blank=True),
        'date_suppression': models.DateField("Date de suppression automatique",
                                             null=True, blank=True),
        'user': models.ForeignKey(custom.CustomUser, related_name='models',
                                  on_delete=models.PROTECT,
                                  help_text="Utilisateur abonné"),
        'project': models.ForeignKey(custom.Project, related_name='models',
                                    on_delete=models.PROTECT,
                                    help_text="Projet"),
        '__str__': lambda self: '%s %s' (self.title),
        }

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

    # creation modele
    model = create_model(projet.slug + '_' + feature, fields,
                         app_label=APP_NAME,
                         module=module,
                         admin_opts={})

    try:
        with connection.schema_editor() as editor:
            editor.create_model(model)
        return {'success': "Votre signalement a été crée avec succès"}
    except Exception as e:
        return {'error': "Une erreur s'est produite, veuillez renouveller votre demande ultérieurement"}
