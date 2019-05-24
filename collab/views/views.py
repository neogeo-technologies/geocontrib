from collab import models
from collab.choices import STATUS
from collab.choices import USER_TYPE
from collab.choices import USER_TYPE_ARCHIVE
from collab.db_utils import commit_data
from collab.forms import ProjectForm
from collab.views.project_services import generate_feature_id
from collab.views.project_services import get_feature
from collab.views.project_services import get_feature_detail
from collab.views.project_services import get_last_features
from collab.views.project_services import get_project_features
# from collab.views.project_services import get_project_feature_geom_type
from collab.views.project_services import last_user_registered
from collab.views.project_services import project_feature_type_fields
from collab.views.project_services import project_feature_number
from collab.views.project_services import project_features_types

from collections import OrderedDict
import datetime
from datetime import timedelta
import dateutil.parser

from django.db.models import Q
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Point
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
import logging

APP_NAME = __package__.split('.')[0]


def get_anonymous_rights(project):
    """
        Return anonymous user rights
        LEVEL = (
            # ('0', 'Utilisateur anonyme'),
            ('1', 'Utilisateur connecté'),
            ('2', "Contribution"),
            ('3', 'Modération'),
            ('4', "Administration"),
        )
    """
    user_right = {'proj_creation': False,
                  'proj_modification': False,
                  'proj_consultation': False,
                  'feat_archive': False,
                  'feat_creation': False,
                  'feat_modification': False,
                  'feat_consultation': False,
                  'user_admin': False,
                  'model_creation': False}
    # visible to anonymous user if feature are visible
    if int(project.visi_feature) == 0:
        user_right['proj_consultation'] = True
        user_right['feat_consultation'] = True
    if int(project.visi_archive) == 0:
        user_right['feat_archive'] = True
    return user_right


class LoginView(TemplateView):

    template_name = 'collab/registration/login.html'

    def post(self, request, **kwargs):
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        return render(request, self.template_name)

    def get(self, request, **kwargs):
        return render(request, self.template_name)


class LogoutView(TemplateView):

    template_name = 'collab/registration/login.html'

    def get(self, request, **kwargs):
        logout(request)
        return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)


def index(request):
    """
        Main page with the current available projects
    """

    # list of projects
    data = models.Project.objects.values()
    projects = []
    for elt in data:
        project = models.Project.objects.get(slug=elt['slug'])

        # get user right on project
        if request.user.is_authenticated:
            elt['rights'] = request.user.project_right(project)
        else:
            elt['rights'] = get_anonymous_rights(project)

        if not elt['rights'].get("proj_consultation"):
            continue

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

        # illustration url
        if project.illustration:
            elt['illustration_url'] = project.illustration.url

        projects.append(elt)

    context = {
        "title": "Collab",
        "projects": projects,
    }
    return render(request, 'collab/index.html', context)


def get_project_fields(project_slug):

    data = models.Project.objects.filter(slug=project_slug).values(
                                'description', 'illustration', 'title',
                                'creation_date', 'moderation', 'visi_feature' ,
                                'visi_archive', 'archive_feature',
                                'delete_feature', 'slug')
    labels = {
        'description': 'Description',
        'illustration': 'Illustration',
        'title': "Titre",
        'creation_date': 'Date de création',
        'moderation': 'Moderation',
        'visi_feature': "Visibilité des signalements publiés",
        'visi_archive': "Visibilité des signalements archivés",
        'archive_feature': "Délai avant archivage",
        'delete_feature': "Délai avant suppression",
    }
    if data:
        # visi_archive
        id = int(data[0]['visi_archive'])
        data[0]['visi_archive'] = USER_TYPE_ARCHIVE[id][1]
        # visi_feature
        id = int(data[0]['visi_feature'])
        data[0]['visi_feature'] = USER_TYPE[id][1]

    return data, labels


@method_decorator([csrf_exempt], name='dispatch')
class ProjectAdminView(View):
    """
        View to administrate a project
    """

    def get(self, request, project_slug):
        """
            Get the detail of project fields and edit it
        """
        project = get_object_or_404(models.Project,
                                    slug=project_slug)
        # get user right on project
        if request.user.is_authenticated:
            rights = request.user.project_right(project)
        else:
            rights = get_anonymous_rights(project)
        data, labels = get_project_fields(project_slug)
        if data:
            if request.is_ajax():
                context = {
                    "project": project,
                    "edit": True,
                    "user_type_archive": USER_TYPE_ARCHIVE,
                    "user_type": USER_TYPE,
                    "rights": rights,
                    "labels": labels
                }
                return render(request, 'collab/project/project_form.html', context)
            else:
                context = {
                    "project": project,
                    "data": OrderedDict(sorted(data[0].items())),
                    "rights": rights,
                    "labels": labels
                }
                return render(request, 'collab/project/admin_project.html', context)
        else:
            context = {
                "rights": rights
            }
            return render(request, 'collab/project/admin_project.html', context)


    def post(self, request, project_slug):
        """
            View to save modification done to a project
        """
        project = get_object_or_404(models.Project,
                                    slug=project_slug)
        # get user right on project
        if request.user.is_authenticated:
            rights = request.user.project_right(project)
        else:
            rights = get_anonymous_rights(project)
        # update forms fields
        form_data = request.POST.dict()
        form_data.pop('csrfmiddlewaretoken', None)
        if 'moderation' in form_data:
            setattr(project, 'moderation', True)
            form_data.pop('moderation', None)
        else:
            setattr(project, 'moderation', False)
        # update image field
        if 'illustration' in request.FILES:
            setattr(project, 'illustration', request.FILES.get('illustration'))
        form_data.pop('illustration', None)

        for key, value in form_data.items():

            if key == "creation_date":
                creation_date = timezone.make_aware(dateutil.parser.parse(value), timezone.get_current_timezone())
                setattr(project, key, creation_date)
                project.save()
            elif key == "archive_feature" or key == "delete_feature":
                setattr(project, key, timedelta(days=int(value)))
            else:
                setattr(project, key, value)
            project.save()
        project.save()
        # display detail of project
        data, labels = get_project_fields(project_slug)
        context = {
            "project": project,
            "data": OrderedDict(sorted(data[0].items())),
            "rights": rights,
            "labels": labels
        }

        return render(request, 'collab/project/project_detail.html', context)


class ProjectView(FormView):
    template_name = 'collab/project/add_project.html'
    form_class = ProjectForm
    success_url = 'collab/project/add_project.html'

    def form_valid(self, form):

        # Vérifie qu'un projet avec ce titre n'existe pas déjà
        projects_with_this_title = models.Project.objects.filter(title__iexact=form.cleaned_data['title'])
        if projects_with_this_title:
            context = {'errors':
                           {'erreur':
                                ["Veuillez modifier le titre de votre projet, un projet avec ce titre existe déjà."]},
                       'form': form}
            return render(self.request, self.template_name, context)

        result = form.create_project()
        db_error = result.get("db_error")
        if db_error:
            context = {'errors':
            {"Une erreur s'est produite": [db_error]}, 'form': form}
            return render(self.request, self.template_name, context)
        return redirect('project', project_slug=result["project"].slug)

    def form_invalid(self, form):
        errors = form.errors.copy()
        for key, val in form.errors.items():
            label = form.fields[key].label
            errors[label] = errors.pop(key, None)
        context = {'errors': errors, 'form': form}
        return render(self.request, self.template_name, context)


def my_account(request):

    if request.user.is_authenticated:
        auth_proj = []
        project_info = {}

        # open project (can be visualize by anonymous or connected user)
        if request.user.is_superuser:
            project_list = models.Project.objects.all()
        else:
            # retrieve user project
            for elt in models.Autorisation.objects.filter(
                       user=request.user):
                project = models.Project.objects.get(id=elt.project.id)
                auth_proj.append(project)
                project_info[project.slug] = {"level": elt.get_level_display()}
                project_list = list(set(auth_proj + list(models.Project.objects.filter(
                             Q(visi_feature='0') | Q(visi_feature='1')))))
        # user info
        user = {"username": request.user.username,
                "name": """{first_name} {last_name}""".format(
                                  first_name=request.user.first_name,
                                  last_name=request.user.last_name),
                "email": request.user.email,
                "is_admin": request.user.is_superuser}

        for project in project_list:
            # recuperation du nombre de contributeur
            nb_contributors = models.Autorisation.objects.filter(
                                        project__slug=project.slug,
                                        level="1").count()
            # recuperation du nombre de commentaire
            nb_comments = models.Comment.objects.filter(project=project).count()
            # get number of feature per project
            list_features = project_features_types(APP_NAME, project.slug)
            nb_features = 0
            for feature_type in list_features:
                nb_features += int(project_feature_number(APP_NAME,
                                   project.slug,
                                   feature_type))
            if not project.slug in project_info:
                if request.user.is_superuser:
                    project_info[project.slug] = {'level': 'SuperAdmin'}
                else:
                    project_info[project.slug] = {'level': 'Aucun'}
            project_info[project.slug].update({'nb_features': nb_features,
                                               'nb_contributors': nb_contributors,
                                               'nb_comments': nb_comments})
        context = {"project_list": project_list, "user": user,
                   "project_info": project_info}
        return render(request, 'collab/my_account.html', context)
    else:
        context = {"error": "Vous n'avez pas les droits nécessaires pour acceder à cette page"}
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
        # get user right on project
        if request.user.is_authenticated:
            rights = request.user.project_right(project)
        else:
            rights = get_anonymous_rights(project)
        # type of features
        features_types = project_features_types(APP_NAME, project_slug)
        if not features_types:
            context = {"message": "Veuillez créer un type de signalement pour ce projet",
                       "rights": rights}
            return render(request, 'collab/feature/add_feature.html', context)
        # type of features's fields
        if request.GET.get('name'):
            res = project_feature_type_fields(APP_NAME, project_slug, request.GET.get('name'))
        else:
            res = project_feature_type_fields(APP_NAME, project_slug, features_types[0])
        # add info for JS display
        if res.get('status', ''):
            # char list
            res['status']['info'] = STATUS
        if request.is_ajax():
            # recuperation des champs descriptifs
            geom_type = project.get_geom(request.GET.get('name'))
            labels = project.get_labels(request.GET.get('name'))
            context = {"res": res.items,
                       "geom_type": geom_type,
                       "rights": rights, "labels": labels}
            return render(request, 'collab/feature/form_body.html', context)
        else:
            # recuperation des champs descriptifs
            geom_type = project.get_geom(features_types[0])
            labels = project.get_labels(features_types[0])
            context = {"project": project, "features_types": features_types,
                       "rights": rights, "labels": labels,
                       "geom_type": geom_type,
                       "res": res.items}
            return render(request, 'collab/feature/add_feature.html', context)

    def post(self, request, project_slug):

        project = get_object_or_404(models.Project,
                                    slug=project_slug)
        # get user right on project
        if request.user.is_authenticated:
            rights = request.user.project_right(project)
        else:
            rights = get_anonymous_rights(project)
        data = request.POST.dict()
        table_name = """{app_name}_{project_slug}_{feature}""".format(
                        app_name=APP_NAME,
                        project_slug=project_slug,
                        feature=data.get('feature', ''))
        user_id = request.user.id
        creation_date = datetime.datetime.now()
        feature_id = generate_feature_id(APP_NAME, project_slug, data.get('feature', ''))
        # remove the csrfmiddlewaretoken key
        data.pop('csrfmiddlewaretoken', None)
        data.pop('feature', None)

        # get comment
        comment = data.pop('comment', None)
        # get geom
        try:
            geom = GEOSGeometry(data.pop('geom', None), srid=settings.DB_SRID)
        except Exception as e:
            context = {"error": "le fromat de votre géométrue est incorrect",
                       "rights": rights}
            return render(request, 'collab/feature/form_body.html', context)

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
        sql = """INSERT INTO "{table}" (creation_date, modification_date, user_id, project_id,
                 feature_id, geom {data_keys})
                 VALUES ('{creation_date}','{modification_date}','{user_id}','{project_id}',
                 '{feature_id}', '{geom}' {data_values});""".format(
                 creation_date=creation_date,
                 modification_date=creation_date,
                 project_id=project.id,
                 user_id=user_id,
                 table=table_name,
                 feature_id=feature_id,
                 data_keys=data_keys,
                 data_values=data_values,
                 geom=geom)
        creation = commit_data('default', sql)
        # create comment
        obj = models.Comment.objects.create(author=request.user,
                                            feature_id=feature_id,
                                            comment=comment, project=project)
        # recuperation des champs descriptifs
        if creation == True:
            context = {"rights": rights, "project": project, 'success': 'Le signalement a bien été ajouté'}
            return render(request, 'collab/feature/form_body.html', context)
        else:
            msg = "Une erreur s'est produite, veuillez renouveller votre demande ultérieurement"
            logger = logging.getLogger(__name__)
            logger.exception(msg)
            context = {"rights": rights, "project": project, 'error': msg}
            return render(request, 'collab/feature/add_feature.html', context)


def project(request, project_slug):
    """
        Display the detail of a specific project
    """
    # Recuperation du projet
    project = get_object_or_404(models.Project,
                                slug=project_slug)
    # get user right on project
    if request.user.is_authenticated:
        rights = request.user.project_right(project)
    else:
        rights = get_anonymous_rights(project)
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
               "last_features": last_features,
               "rights": rights}
    return render(request, 'collab/project/project_home.html', context)


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
    # get user right on project
    if request.user.is_authenticated:
        rights = request.user.project_right(project)
    else:
        rights = get_anonymous_rights(project)
    # list of feature per project
    feature_type = project_features_types(APP_NAME, project_slug)
    feature_list = OrderedDict()
    # get list of feature per project
    for feature_type in feature_type:
        feature_list[feature_type] = get_project_features(APP_NAME,
                                                          project_slug,
                                                          feature_type)
    context = {'rights': rights, 'project': project, 'feature_list': feature_list}
    return render(request, 'collab/feature/feature_map.html', context)


def project_feature_list(request, project_slug):
    """
        Display the list of the available features for a
        given project
    """

    # get project
    project = get_object_or_404(models.Project,
                                slug=project_slug)
    # get user right on project
    if request.user.is_authenticated:
        rights = request.user.project_right(project)
    else:
        rights = get_anonymous_rights(project)
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
            if elt.get('status', ''):
                elt['status'] = STATUS[int(elt['status'])][1]
            if elt.get('user_id', ''):
                elt['utilisateur'] = elt.pop('user_id', None)
                try:
                    elt['utilisateur'] = models.CustomUser.objects.get(
                                         id=elt['utilisateur'])
                except Exception as e:
                    elt['utilisateur'] = 'Anonyme'

    context = {'rights': rights, 'project': project, 'feature_list': feature_list}

    return render(request, 'collab/feature/feature_list.html', context)


class ProjectFeatureDetail(View):

    def get(self, request, project_slug, feature_type, feature_pk):
        """
            Display the detail of a given feature
            @param
            @return JSON
        """
        project, feature = get_feature_detail(APP_NAME, project_slug, feature_type, feature_pk)
        labels = project.get_labels(feature_type)
        # get user right on project
        if request.user.is_authenticated:
            rights = request.user.project_right(project)
        else:
            rights = get_anonymous_rights(project)
        # get feature comment
        comments = list(models.Comment.objects.filter(project=project,
                                                feature_id=feature.get('feature_id','')
                                                ).values('comment',
                                                'author__first_name',
                                                'author__last_name',
                                                'creation_date'))
        context = {'rights': rights, 'project': project,
                   'feature': feature, 'comments': comments, 'labels': labels}
        return render(request, 'collab/feature/feature_detail.html', context)

    def post(self, request, project_slug, feature_type, feature_pk):
        """
            Add feature comment
            @param
            @return JSON
        """
        comment = request.POST.get('comment', '')
        project, feature = get_feature_detail(APP_NAME, project_slug,
                                              feature_type, feature_pk)
        # get user right on project
        if request.user.is_authenticated:
            rights = request.user.project_right(project)
        else:
            rights = get_anonymous_rights(project)
        # create comment
        obj = models.Comment.objects.create(author=request.user,
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
        context = {'rights': rights, 'project': project, 'feature': feature, 'comments': comments}
        return render(request, 'collab/feature/feature_detail.html', context)

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
