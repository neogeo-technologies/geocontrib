from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.core.management import call_command
from django.db import connection
from django.db.models import Manager as GeoManager
from django.http import JsonResponse
from django.shortcuts import render
import io
import uuid
import shutil
from collab import models as custom
from hashlib import md5
from ..actions import create_model

APP_NAME = __package__.split('.')[0]


def add_feature_model(request):

    if request.method == 'POST':

        if request.POST.getlist('field_type') and request.POST.getlist('field_name') \
           and request.POST.getlist('project') and request.POST.getlist('feature'):

            message = generate_feature_model(request.POST.get('project'),
                                             request.POST.get('feature'),
                                             request.POST.getlist('field_name'),
                                             request.POST.getlist('field_type'),
                                             request.user)
            context = {'message': message}
            return render(request, APP_NAME + '/add_feature_model.html',
                          context=context)
        else:
            context = {'message': message}
            return render(request, APP_NAME + '/add_feature_model.html',
                          context=context)
    else:
        projects = custom.Project.objects.all()
        context = {'projects': projects}
        return render(request, APP_NAME + '/add_feature_model.html',
                      context=context)


def generate_feature_model(projet_id, feature, names, types, user):

    # Récuperation du nom du projet
    projet = custom.Project.objects.get(id=projet_id)

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
                                   choices=custom.STATUS,
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

    # ajout du nom de la table
    table_name = APP_NAME + "_" + projet.slug + '_' + feature

    # creation modele
    model = create_model(projet.slug + '_' + feature, fields,
                         app_label=APP_NAME,
                         module=module,
                         admin_opts={})

    try:
        with connection.schema_editor() as editor:
            editor.create_model(model)

        if not projet.feature_type:
            projet.feature_type = [{'table_name': table_name,
                                   'feature': feature,
                                   'user_id': user.id,
                                   'username': user.username}]
        else:
            projet.feature_type.append({'table_name': table_name,
                                   'feature': feature,
                                   'user_id': user.id,
                                   'username': user.username})
        projet.save()
        # generation du fichier models.py
        # out = io.StringIO()
        # call_command('inspectdb', table_name, stdout=out)
        #
        # # A AMELIORER GESTION FK ajout du nom du projet par inspectdb....
        # out = out.getvalue().replace('CollabProject', 'Project').replace(
        #                              'CollabCustomuser', 'CustomUser').replace(
        #                              'CollabStatus', 'Status')
        #
        # with open(APP_NAME + """/models/models_feature_{feature_type}.py""".format(
        #           feature_type=feature), 'a') as fd:
        #     fd.write(out)

        return "Votre demande a bien été prise en compte, votre signalement sera bientôt disponible"
    except Exception as e:
        return "Une erreur s'est produite, veuillez renouveller votre demande ultérieurement"
