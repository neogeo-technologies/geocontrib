import uuid
from collab import models
from collab.choices import STATUS
from collab.choices import STATUS_MODERE
from collab.choices import USER_TYPE
from collab.choices import USER_TYPE_ARCHIVE
from collab.db_utils import commit_data
from collab.db_utils import create_feature_sql
from collab.db_utils import edit_feature_sql
from collab.forms import ProjectForm

from collab.views.user_services import get_last_user_comments
from collab.views.user_services import get_last_user_feature
from collab.views.user_services import get_last_user_registered
from collab.views.user_services import get_user_feature

# from collab.views.project_services import generate_feature_id
# from collab.views.project_services import get_feature
from collab.views.project_services import get_feature_detail
from collab.views.project_services import get_feature_pk
# from collab.views.project_services import get_feature_uuid
from collab.views.project_services import get_last_features
from collab.views.project_services import get_project_features
from collab.views.project_services import project_feature_type_fields
from collab.views.project_services import project_feature_number
from collab.views.project_services import project_features_types

from collab.views.validation_services import validate_geom

from collections import OrderedDict
import datetime
from datetime import timedelta
import dateutil.parser

# from django.db.models import Q
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import GEOSGeometry
from django.http import HttpResponseRedirect
# from django.http import JsonResponse
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
        return redirect('project', project_slug=project_slug)


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
        rights = {}
        project_info = {}

        project_list = models.Project.objects.all()
        for elt in project_list:
            if request.user.is_authenticated:
                rights[elt.slug] = request.user.project_right(elt)
            else:
                rights[elt.slug] = get_anonymous_rights(elt)

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
        # get 3 last user comments
        last_comment = get_last_user_comments(request.user, 3)
        # get feature pk
        feature_pk = {}
        for elt in last_comment:
            table_name = """{app_name}_{project_slug}_{feature_type_slug}""".format(
                            app_name=APP_NAME,
                            project_slug=elt.project.slug,
                            feature_type_slug=elt.feature_type_slug)
            feature_pk[elt.feature_id] = get_feature_pk(table_name, elt.feature_id)
        # get 3 last user feature
        tables_names = get_user_feature(APP_NAME, request.user)
        features = []
        for elt in tables_names:
            data = get_last_user_feature(request.user, APP_NAME,
                                         elt['project'], elt['feature_type_slug'])
            if data:
                features.append(data)
        features.sort(key=lambda item: item['modification_date'], reverse=True)
        if len(features) > 3:
            features = features[0:3]
        context = {"project_list": project_list, "rights": rights, "user": user,
                   "feature_pk": feature_pk, "project_info": project_info,
                   "last_comment": last_comment, "features": features}
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
        @return Comment
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
            context = {"error": "Veuillez créer un type de signalement pour ce projet",
                       "project": project,
                       "rights": rights}
            return render(request, 'collab/feature/add_feature.html', context)
        # type of features's fields
        if request.GET.get('name'):
            res = project_feature_type_fields(APP_NAME, project_slug, request.GET.get('name'))
        else:
            res = project_feature_type_fields(APP_NAME, project_slug, features_types[0])

        # add info for JS display : do not display the same status depending on project configuration
        if res.get('status', '') and (rights['feat_modification'] == True or project.moderation == False):
            res['status']['choices'] = STATUS
        elif res.get('status', '') and project.moderation == True:
            res['status']['choices'] = STATUS_MODERE

        if request.is_ajax():
            # recuperation des champs descriptifs
            geom_type = project.get_geom(request.GET.get('name'))
            labels = project.get_labels(request.GET.get('name'))
            context = {"res": res.items,
                       "geom_type": geom_type,
                       "rights": rights, "labels": labels}
            return render(request, 'collab/feature/create_feature.html', context)
        else:
            # recuperation des champs descriptifs
            geom_type = project.get_geom(features_types[0])
            labels = project.get_labels(features_types[0])
            context = {"project": project, "features_types": features_types,
                       "rights": rights, "labels": labels,
                       "geom_type": geom_type,
                       "res": res.items}
            # A AMELIORER
            if request.session.get('error', ''):
                context['error'] = request.session.pop('error', '')
            return render(request, 'collab/feature/add_feature.html', context)

    def post(self, request, project_slug):
        project = get_object_or_404(models.Project, slug=project_slug)
        # get user right on project
        if request.user.is_authenticated:
            rights = request.user.project_right(project)
        else:
            rights = get_anonymous_rights(project)
        data = request.POST.dict()
        feature_type_slug = data.get('feature', '')
        table_name = """{app_name}_{project_slug}_{feature_type_slug}""".format(
                        app_name=APP_NAME,
                        project_slug=project_slug,
                        feature_type_slug=feature_type_slug)
        user_id = request.user.id
        creation_date = datetime.datetime.now()
        # feature_id = generate_feature_id(APP_NAME, project_slug, data.get('feature', ''))
        feature_id = str(uuid.uuid4())
        # get geom
        data_geom = data.pop('geom', None)
        geom, msg = validate_geom(data_geom, feature_type_slug, project)
        if msg:
            request.session['error'] = msg
            return redirect('project_add_feature', project_slug=project_slug)

        # get comment
        comment = data.pop('comment', None)
        # get sql for additonal field
        data_keys, data_values = create_feature_sql(data)
        # create feature
        sql = """INSERT INTO "{table}" (feature_id, creation_date,
            modification_date, user_id, project_id, geom {data_keys})
            VALUES ('{feature_id}', '{creation_date}', '{modification_date}',
            '{user_id}', '{project_id}', '{geom}' {data_values});""".format(
            feature_id=feature_id,
            creation_date=creation_date,
            modification_date=creation_date,
            project_id=project.id,
            user_id=user_id,
            table=table_name,
            data_keys=data_keys,
            data_values=data_values,
            geom=geom)

        creation = commit_data('default', sql)
        if comment and creation:
            # create comment
            obj = models.Comment.objects.create(author=request.user,
                                                feature_id=feature_id,
                                                feature_type_slug=feature_type_slug,
                                                comment=comment, project=project)

            # Ajout d'un evenement de création d'un commentaire:
            models.Event.objects.create(
                user=request.user,
                event_type='create',
                object_type='comment',
                project_slug=project.slug,
                feature_id=feature_id,
                comment_id=obj.comment_id,
                feature_type_slug=feature_type_slug,
                data={}
            )

        # recuperation des champs descriptifs
        if creation == True:
            # @cbenhabib on passe par le feature_id
            # feature_pk = get_feature_pk(table_name, feature_id)

            # Ajout d'un evenement de création d'un signalement:
            models.Event.objects.create(
                user=request.user,
                event_type='create',
                object_type='feature',
                project_slug=project.slug,
                feature_id=feature_id,
                feature_type_slug=feature_type_slug,
                data={}
            )

            return redirect('project_feature_detail', project_slug=project_slug,
                            feature_type_slug=feature_type_slug, feature_id=feature_id)
        else:
            msg = "Une erreur s'est produite, veuillez renouveller votre demande ultérieurement"
            logger = logging.getLogger(__name__)
            logger.exception(msg)
            request.session['error'] = msg
            return redirect('project_add_feature', project_slug=project_slug)



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
    users = get_last_user_registered(project_slug)
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
                elt['author'] = elt.pop('user_id', None)
                try:
                    elt['author'] = models.CustomUser.objects.get(
                                         id=elt['author'])
                except Exception as e:
                    elt['author'] = 'Anonyme'

    context = {'rights': rights, 'project': project, 'feature_list': feature_list}

    return render(request, 'collab/feature/feature_list.html', context)


class ProjectFeatureDetail(View):

    def get(self, request, project_slug, feature_type_slug, feature_id):
        """
            Display the detail of a given feature
            @param
            @return JSON
        """
        project, feature, user = get_feature_detail(APP_NAME, project_slug, feature_type_slug, feature_id)
        labels = project.get_labels(feature_type_slug)
        # get user right on project
        if request.user.is_authenticated:
            rights = request.user.project_right(project)
        else:
            rights = get_anonymous_rights(project)
        # get feature comment
        comments = list(
            models.Comment.objects.filter(
                project=project, feature_id=feature.get('feature_id', '')
            ).values(
                'comment', 'author__first_name', 'author__last_name',
                'creation_date', 'comment_id'))

        com_attachment = {}
        for com in comments:
            try:
                obj_comment = models.Comment.objects.get(comment_id=com.get('comment_id', ''))
                obj_attachment = models.Attachment.objects.get(comment=obj_comment)
                com_attachment[com.get('comment_id', '')] = obj_attachment.__dict__
                com_attachment[com.get('comment_id', '')].update({'url': obj_attachment.file.url})
            except Exception as e:
                pass
        # get feature attachment
        attachments = list(models.Attachment.objects.filter(project=project,
                                                feature_id=feature.get('feature_id', '')))
        context = {'rights': rights, 'project': project, 'author': user,
                   'comments': comments, 'attachments': attachments,
                   'com_attachment': com_attachment,
                   'file_max_size': settings.FILE_MAX_SIZE,
                   'labels': labels, 'img_format': settings.IMAGE_FORMAT}
        # A AMELIORER
        if not request.is_ajax() or request.session.get('error', ''):
            if request.session.get('error', ''):
                context['error'] = request.session.pop('error', '')
            geom_to_wkt = feature.get('geom', '')
            feature['geom'] = GEOSGeometry(geom_to_wkt).wkt
            context['feature'] = feature
            return render(request, 'collab/feature/feature.html', context)
        # if request is ajax
        elif request.is_ajax():
            # type of features's fields
            data = project_feature_type_fields(APP_NAME, project_slug, feature_type_slug)
            for key, val in data.items():
                if key == 'geom':
                    data[key]['value'] = GEOSGeometry(feature.get(key, '')).wkt
                else:
                    data[key]['value'] = feature.get(key, '')
                # add info for JS display : do not display the same status depending on project configuration
                if key == 'status':
                    if rights['feat_modification'] == True or project.moderation == False:
                        data[key]['choices'] = STATUS
                    elif project.moderation == True:
                        data[key]['choices'] = STATUS_MODERE
            context['feature'] = data
            context['edit'] = True
            # type de géometrie
            context['geom_type'] = project.get_geom(feature_type_slug)
            return render(request, 'collab/feature/edit_feature.html', context)

    def post(self, request, project_slug, feature_type_slug, feature_id):
        """
            Modify feature fields
            @param
            @return JSON
        """
        project = get_object_or_404(models.Project,
                                    slug=project_slug)
        # get user right on project
        data = request.POST.dict()
        table_name = """{app_name}_{project_slug}_{feature_type_slug}""".format(
                        app_name=APP_NAME,
                        project_slug=project_slug,
                        feature_type_slug=feature_type_slug)

        modification_date = datetime.datetime.now()
        # get geom
        data_geom = data.pop('geom', None)
        geom, msg = validate_geom(data_geom, feature_type_slug, project)
        if msg:
            request.session['error'] = msg
            return redirect('project_feature_detail', project_slug=project_slug,
                            feature_type_slug=feature_type_slug, feature_id=feature_id)

        # get comment
        comment = data.pop('comment', None)

        # get sql for additonal field
        add_sql = edit_feature_sql(data)
        # # create with basic keys
        sql = """UPDATE "{table}"
                 SET  modification_date='{modification_date}',
                      geom='{geom}' {add_sql}
                 WHERE feature_id='{feature_id}';""".format(
                 modification_date=modification_date,
                 table=table_name,
                 feature_id=feature_id,
                 add_sql=add_sql,
                 geom=geom)

        creation = commit_data('default', sql)
        if creation == True:
            return redirect('project_feature_detail', project_slug=project_slug,
                            feature_type_slug=feature_type_slug, feature_id=feature_id)
        else:
            msg = "Une erreur s'est produite, veuillez renouveller votre demande ultérieurement"
            logger = logging.getLogger(__name__)
            logger.exception(creation)
            request.session['error'] = msg
            return redirect('project_feature_detail', project_slug=project_slug,
                            feature_type_slug=feature_type_slug, feature_id=feature_id)


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
