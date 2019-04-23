from collab import models
from collab.db_utils import commit_data
from collab.views.project_services import generate_feature_id
from collab.views.project_services import get_last_features
from collab.views.project_services import last_user_registered
from collab.views.project_services import project_feature_fields
from collab.views.project_services import project_feature_number
from collab.views.project_services import project_features_types
from collab.views.project_services import get_project_features
import datetime
from django.core import serializers
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views import View
import json


APP_NAME = __package__.split('.')[0]

dummy_projects = {
    "l49": {
        "id": "l49",
        "title": "L49",
        "description": "Publication de la localisation de travaux planifiés sur la voie publique en vue de "
                       "l'application de l'article L49 du Code des postes et des communications électroniques.",
        "illustration": "http://www.montpellier3m.fr/sites/default/files/vignettes/actualite/travaux_2.jpg",
        "min_access_level_for_published_issues": "anonymous",
        "date_creation": datetime.date(2014, 8, 24),
        "is_moderated": False,
        "nb_of_contributors": 13,
        "nb_of_issues": 134,
        "nb_of_comments": 3,
    },
    "adresses": {
        "id": "adresses",
        "title": "Adresses",
        "description": "Identification des erreurs ou absences dans les bases d'adresse de référence. Les signalements "
                       "recueillis concernent aussi bien les erreurs de localisation, de numérotation et de "
                       "dénomination.",
        "illustration": "https://www.rapid-sign.com/ori-numeros-de-maison-noir-13cm-74.jpg",
        "min_access_level_for_published_issues": "connected",
        "date_creation": datetime.date(2012, 4, 12),
        "is_moderated": False,
        "nb_of_contributors": 32,
        "nb_of_issues": 152,
        "nb_of_comments": 223,
    },
    "ortho-2018": {
        "id": "ortho-2018",
        "title": "Ortho 2018",
        "description": "Identification des non-conformités de l'ortho 2018 par rapport à ses spécifications&nbsp;: "
                       "précision planimétrique, radiométrie, colorimétrie...",
        "illustration": "https://www.geopicardie.fr/geoserver/geopicardie/ows?SERVICE=WMS&LAYERS=picardie_ortho_ign_2013_vis&TRANSPARENT=true&VERSION=1.3.0&FORMAT=image%2Fpng&EXCEPTIONS=XML&REQUEST=GetMap&STYLES=&SLD_VERSION=1.1.0&CRS=EPSG%3A3857&BBOX=276314.73430822,6307626.8969942,276950.11710584,6308262.2797919&WIDTH=532&HEIGHT=532",
        "min_access_level_for_published_issues": "contributor",
        "date_creation": datetime.date(2018, 9, 23),
        "is_moderated": False,
        "nb_of_contributors": 5,
        "nb_of_issues": 28,
        "nb_of_comments": 41,
    },
    "occupation-du-sol-2d": {
        "id": "occupation-du-sol-2d",
        "title": "Occupation du sol 2D",
        "description": "Identification des anomalies présentes dans la base de l'occupation du sol 2D issues d'erreur "
                       "flagrantes de photo-interprétation.",
        "illustration": "https://www.geopicardie.fr/geoserver/geopicardie/ows?SERVICE=WMS&LAYERS=mos_picardie&EXCEPTIONS=XML&FORMAT=image%2Fpng&TRANSPARENT=TRUE&VERSION=1.3.0&SLD_VERSION=1.1.0&REQUEST=GetMap&STYLES=&CRS=EPSG%3A3857&BBOX=284696.53219112,6305613.2590304,294862.65695304,6315779.3837923&WIDTH=532&HEIGHT=532",
        "min_access_level_for_published_issues": "contributor",
        "date_creation": datetime.date(2018, 5, 4),
        "is_moderated": False,
        "nb_of_contributors": 12,
        "nb_of_issues": 41,
        "nb_of_comments": 109,
    },
    "decheteries": {
        "id": "decheteries",
        "title": "Déchèteries",
        "description": "Lacolisation des déchèteries en Région Hauts-de-France.",
        "illustration": "https://image.freepik.com/photos-gratuite/closeup-mains-separer-bouteilles-plastique_53876-46918.jpg",
        "min_access_level_for_published_issues": "anonymous",
        "date_creation": datetime.date(2018, 5, 4),
        "is_moderated": True,
        "nb_of_contributors": 20,
        "nb_of_issues": 131,
        "nb_of_comments": 12,
    },
}


def index(request):
    """
        Main page with the current available projects
    """
    # list of projects
    data = models.Project.objects.values()
    for elt in data:
        # import pdb; pdb.set_trace()
        project = models.Project.objects.get(slug=elt['slug'])
        elt['visi_feature_name'] = project.get_visi_feature_display()
        # recuperation du nombre de contributeur
        elt['nb_contributors'] = models.Autorisation.objects.filter(
                                    project__slug=elt['slug'],
                                    level="1").count()
        # get number of feature per project
        list_features = project_features_types(APP_NAME, elt['slug'])
        nb_features = 0
        for feature_name in list_features:
            nb_features += int(project_feature_number(APP_NAME,
                              elt['slug'],
                              feature_name))

        elt['nb_features'] = nb_features

    context = {
        "title": "Collab",
        "projects": list(data),
    }
    return render(request, 'collab/index.html', context)


def my_account(request):
    context = {"title": "My account"}
    return render(request, 'collab/my_account.html', context)


def legal(request):
    context = {"title": "Mentions légales"}
    return render(request, 'collab/legal.html', context)


def site_help(request):
    context = {"title": "Aide"}
    return render(request, 'collab/help.html', context)


class ProjectFeature(View):
    """
        Function to add a feature to a project
        @param
        @return JSON
    """
    def get(self, request, project_slug):

        project = get_object_or_404(models.Project,
                                    slug=project_slug)
        # type of features
        features_types = project_features_types(APP_NAME, project_slug)
        # type of features's fields
        res = {}
        for elt in features_types:
            res[elt] = project_feature_fields(APP_NAME, project_slug, elt)
        if not features_types:
            context = {"message": "Veuillez creer un type de signalement pour ce projet"}
            return render(request, 'collab/add_feature.html', context)

        # add info for JS display
        for key, val in res.items():
            if val.get('geom', ''):
                # type of geometry
                val['geom']['info'] = project.get_geom_type_display()
            if val.get('status'):
                # char list
                val['status']['info'] = models.STATUS
        # build contexte for template
        context = {"res": res, "dic_key": features_types[0]}
        return render(request, 'collab/add_feature.html', context)

    def post(self, request, project_slug):

        project = get_object_or_404(models.Project,
                                    slug=project_slug)
        data = request.POST.dict()
        table_name = """{app_name}_{project_slug}_{feature}""".format(
                        app_name=APP_NAME,
                        project_slug=project_slug,
                        feature=data.get('feature', ''))
        user_id = request.user.id
        date_creation = datetime.datetime.now()
        feature_id = generate_feature_id(APP_NAME, project_slug, data.get('feature', ''))
        # remove the csrfmiddlewaretoken key
        try:
            data.pop('csrfmiddlewaretoken')
            data.pop('feature')
        except Exception as e:
            pass
        # add data send by the form
        # remove empty keys
        data = {k: v for k, v in data.items() if v}
        data_keys = ' , '.join(list(data.keys()))
        data_values = "' , '".join(list(data.values()))
        # # create with basic keys
        sql = """INSERT INTO "{table}" (date_creation, date_modification, user_id, project_id, feature_id,{data_keys})
                 VALUES ('{date_creation}','{date_modification}','{user_id}','{project_id}',
                 '{feature_id}','{data_values}');""".format(
                 date_creation=date_creation,
                 date_modification=date_creation,
                 project_id=project.id,
                 user_id=user_id,
                 table=table_name,
                 feature_id=feature_id,
                 data_keys=data_keys,
                 data_values=data_values)
        creation = commit_data('default', sql)
        if creation == True:
            # register the new signal
            context = {'message': 'Le signalement a bien été ajouté'}
            return render(request, 'collab/add_feature.html', context)
        else:
            context = {'message': "Une erreur s'est produite. Veuillez réessayer ultérieurement"}
            return render(request, 'collab/add_feature.html', context)


def project(request, project_slug):

    # Recuperation du projet
    project = get_object_or_404(models.Project,
                                slug=project_slug)
    # recuperation des derniers utilisateurs
    users = last_user_registered(project_slug)
    # recuperation du nombre de contributeur
    nb_contributors = models.Autorisation.objects.filter(
                      project__slug=project_slug,
                      level="1").count()
    # list of feature type per project
    feature_type = project_features_types(APP_NAME, project_slug)
    nb_features = 0
    last_features = {}

    # get list of feature per project
    for feature_name in feature_type:
        # get number of feature per project
        nb_features += int(project_feature_number(APP_NAME,
                           project_slug,
                           feature_name))
        last_features[feature_name] = get_last_features(APP_NAME,
                                                        project_slug,
                                                        feature_name)

    context = {"project": project, "users": users,
               "nb_contributors": nb_contributors,
               "nb_features": nb_features,
               "last_features": last_features}
    return render(request, 'collab/project_home.html', context)


def project_users(request, project_slug):
    # Get project info from slug
    context = {
        "title": "Nom du projet",
        "content": "{} project : users".format(project_slug),
    }
    return render(request, 'collab/empty.html', context)


def project_feature_list(request, project_slug):

    # get project
    project = get_object_or_404(models.Project,
                                slug=project_slug)

    # list of feature per project
    feature_type = project_features_types(APP_NAME, project_slug)
    feature_list = {}
    # get list of feature per project
    for feature_name in feature_type:
        feature_list[feature_name] = get_project_features(APP_NAME,
                                                          project_slug,
                                                          feature_name)

    context = {'project': project, 'feature_list': feature_list}
    return render(request, 'collab/feature_list.html', context)


def project_issue_detail(request, project_slug, issue_id):
    # Get project info from slug
    context = {
        "title": "Nom du projet",
        "content": "{} project : issue detail {}".format(project_slug, issue_id),
    }
    return render(request, 'collab/empty.html', context)


def project_import_issues(request, project_slug):
    # Get project info from slug
    context = {
        "title": "Nom du projet",
        "content": "{} project : import issues".format(project_slug),
    }
    return render(request, 'collab/empty.html', context)


def project_import_geo_image(request, project_slug):
    # Get project info from slug
    context = {
        "title": "Nom du projet",
        "content": "{} project : import geo image".format(project_slug),
    }
    return render(request, 'collab/empty.html', context)


def project_download_issues(request, project_slug):
    # Get project info from slug
    context = {
        "title": "Nom du projet",
        "content": "{} project : download issues".format(project_slug),
    }
    return render(request, 'collab/empty.html', context)
