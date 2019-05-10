from collab import models
from collab.choices import STATUS
from collab.db_utils import commit_data
from collab.forms import ProjectForm
from collab.views.project_services import generate_feature_id
from collab.views.project_services import get_feature
from collab.views.project_services import get_feature_detail
from collab.views.project_services import get_last_features
from collab.views.project_services import get_project_features
from collab.views.project_services import get_project_feature_geom
from collab.views.project_services import last_user_registered
from collab.views.project_services import project_feature_type_fields
from collab.views.project_services import project_feature_number
from collab.views.project_services import project_features_types
from collections import OrderedDict
import datetime
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import FormView

APP_NAME = __package__.split('.')[0]


def index(request):
    """
        Main page with the current available projects
    """
    # list of projects
    data = models.Project.objects.values()
    for elt in data:
        project = models.Project.objects.get(slug=elt['slug'])
        elt['visi_feature_type'] = project.get_visi_feature_display()
        # recuperation du nombre de contributeur
        elt['nb_contributors'] = models.Autorisation.objects.filter(
                                    project__slug=elt['slug'],
                                    level="1").count()
        # recuperation du nombre de commentaire
        elt['nb_comments'] = models.Comment.objects.filter(project=project).count()
        # get number of feature per project
        list_features = project_features_types(APP_NAME, elt['slug'])
        nb_features = 0
        for feature_type in list_features:
            nb_features += int(project_feature_number(APP_NAME,
                              elt['slug'],
                              feature_type))

        elt['nb_features'] = nb_features

    context = {
        "title": "Collab",
        "projects": list(data),
    }
    return render(request, 'collab/index.html', context)


class ProjectView(FormView):
    template_name = 'collab/add_project.html'
    form_class = ProjectForm
    success_url = 'collab/add_project.html'

    def form_valid(self, form):

        # verifie qu'un projet avec ce titre n'existe pas deja
        try:
            project = models.Project.objects.get(title=form.cleaned_data['title'])
            context = {'errors':
            {'erreur': ["""Veuillez modifier le titre de votre application,
            une application avec ce titre existe déjà"""]}, 'form': form}
            return render(self.request, 'collab/add_project.html', context)
        except Exception as e:
            pass
        dberror = form.create_project()
        if dberror:
            context = {'errors':
            {"Une erreur s'est produite": [dberror]}, 'form': form}
            return render(self.request, 'collab/add_project.html', context)
        return render(self.request, 'collab/add_project.html')


    def form_invalid(self, form):
        errors = form.errors.copy()
        for key, val in form.errors.items():
            label = form.fields[key].label
            errors[label] = errors.pop(key)
        context = {'errors': errors, 'form': form}
        return render(self.request, 'collab/add_project.html', context)


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
            res[elt] = project_feature_type_fields(APP_NAME, project_slug, elt)
            # type of geometry
            res[elt].update({'geometry_type': get_project_feature_geom(APP_NAME,
                                                                       project_slug,
                                                                       elt)})
        if not features_types:
            context = {"message": "Veuillez créer un type de signalement pour ce projet"}
            return render(request, 'collab/add_feature.html', context)

        # add info for JS display
        for key, val in res.items():
            if val.get('status'):
                # char list
                val['status']['info'] = STATUS
        if request.is_ajax():
            context = {"res": res.get(request.GET.get('name')).items}
            return render(request, 'collab/form_body.html', context)
        else:
            context = {"project": project, "features_types": features_types}
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
            # get comment
            comment = data.pop('comment')
        except Exception as e:
            pass
        # add data send by the form
        # remove empty keys -> A AMELIORER "'" !!!!!!!!!
        data = {k: v for k, v in data.items() if v}
        data_keys = " "
        data_values = " "
        if data.keys():
            data_keys = ' , ' + ' , '.join(list(data.keys()))
        if data.values():
            data_values = " , '" + "' , '".join(list(data.values())) + "'"
        # # create with basic keys
        sql = """INSERT INTO "{table}" (date_creation, date_modification, user_id, project_id, feature_id {data_keys})
                 VALUES ('{date_creation}','{date_modification}','{user_id}','{project_id}',
                 '{feature_id}' {data_values});""".format(
                 date_creation=date_creation,
                 date_modification=date_creation,
                 project_id=project.id,
                 user_id=user_id,
                 table=table_name,
                 feature_id=feature_id,
                 data_keys=data_keys,
                 data_values=data_values)
        creation = commit_data('default', sql)
        # create comment
        obj, created = models.Comment.objects.get_or_create(author=request.user,
                                             feature_id=feature_id,
                                             comment=comment,
                                             classproject=project)
        if creation == True:
            context = {"project": project, 'success': 'Le signalement a bien été ajouté'}
            return render(request, 'collab/add_feature.html', context)
        else:
            context = {"project": project, 'error': "Une erreur s'est produite. Veuillez réessayer ultérieurement"}
            return render(request, 'collab/add_feature.html', context)


def project(request, project_slug):
    """
        Display the detail of a specific project
    """
    # Recuperation du projet
    project = get_object_or_404(models.Project,
                                slug=project_slug)
    # recuperation des derniers utilisateurs
    users = last_user_registered(project_slug)
    # recuperation du nombre de contributeur
    nb_contributors = models.Autorisation.objects.filter(
                      project__slug=project_slug,
                      level="1").count()
    # recuperation du nombre de commentaire
    comments = models.Comment.objects.filter(project=project).order_by('-creation_date')
    # recuperation du nombre de commentaire
    nb_comments = comments.count()
    comments = comments.values('author__first_name', 'author__last_name',
                               'comment', 'creation_date')
    if comments:
        # get list of last comment
        if nb_comments > 3:
            comments = comments[0:3]
    # list of feature type per project
    feature_type = project_features_types(APP_NAME, project_slug)
    nb_features = 0
    last_features = {}

    # get list of feature per project
    for feature_type in feature_type:
        # get number of feature per project
        nb_features += int(project_feature_number(APP_NAME,
                           project_slug,
                           feature_type))
        last_features[feature_type] = get_last_features(APP_NAME,
                                                        project_slug,
                                                        feature_type, 3)
    context = {"project": project, "users": users,
               "nb_contributors": nb_contributors,
               "nb_features": nb_features,
               "nb_comments": nb_comments,
               "comments": comments,
               "last_features": last_features}
    return render(request, 'collab/project_home.html', context)


def project_users(request, project_slug):
    # Get project info from slug
    context = {
        "title": "Nom du projet",
        "content": "{} project : users".format(project_slug),
    }
    return render(request, 'collab/empty.html', context)


def project_feature_map(request, project_slug):
    """
        Display the list of the available features for a
        given project on a map
    """
    # get project
    project = get_object_or_404(models.Project,
                                slug=project_slug)

    # list of feature per project
    feature_type = project_features_types(APP_NAME, project_slug)
    feature_list = OrderedDict()
    # get list of feature per project
    for feature_type in feature_type:
        feature_list[feature_type] = get_project_features(APP_NAME,
                                                          project_slug,
                                                          feature_type)
    context = {'project': project, 'feature_list': feature_list}
    return render(request, 'collab/feature_map.html', context)


def project_feature_list(request, project_slug):
    """
        Display the list of the available features for a
        given project
    """
    # get project
    project = get_object_or_404(models.Project,
                                slug=project_slug)

    # list of feature per project
    feature_type = project_features_types(APP_NAME, project_slug)
    feature_list = OrderedDict()
    # get list of feature per project
    for feature_type in feature_type:
        feature_list[feature_type] = get_project_features(APP_NAME,
                                                          project_slug,
                                                          feature_type)
    # add info for JS display
    for key, val in feature_list.items():
        for elt in val:
            if elt['status']:
                elt['status'] = STATUS[int(elt['status'])][1]
            if elt['user_id']:
                elt['utilisateur'] = elt.pop('user_id')
                try:
                    elt['utilisateur'] = models.CustomUser.objects.get(
                                         id=elt['utilisateur'])
                except Exception as e:
                    elt['utilisateur'] = 'Anonyme'

    context = {'project': project, 'feature_list': feature_list}

    return render(request, 'collab/feature_list.html', context)


class ProjectFeatureDetail(View):

    def get(self, request, project_slug, feature_type, feature_pk):
        """
            Display the detail of a given feature
            @param
            @return JSON
        """
        project, feature = get_feature_detail(APP_NAME, project_slug, feature_type, feature_pk)
        # get feature comment
        comments = list(models.Comment.objects.filter(project=project,
                                                feature_id=feature['feature_id']
                                                ).values('comment',
                                                'author__first_name',
                                                'author__last_name',
                                                'creation_date'))
        context = {'project': project, 'feature': feature, 'comments': comments}
        return render(request, 'collab/feature_detail.html', context)

    def post(self, request, project_slug, feature_type, feature_pk):
        """
            Add feature comment
            @param
            @return JSON
        """
        comment = request.POST.get('comment', '')
        project, feature = get_feature_detail(APP_NAME, project_slug,
                                              feature_type, feature_pk)
        # create comment
        obj, created = models.Comment.objects.get_or_create(author=request.user,
                                                            feature_id=feature['feature_id'],
                                                            comment=comment,
                                                            project=project)
        # get feature comment
        comments = list(models.Comment.objects.filter(project=project,
                                                      feature_id=feature['feature_id']
                                                      ).values('comment',
                                                      'author__first_name',
                                                      'author__last_name',
                                                      'creation_date'))
        context = {'project': project, 'feature': feature, 'comments': comments}
        return render(request, 'collab/feature_detail.html', context)



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
