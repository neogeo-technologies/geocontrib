import uuid
from collab import models
from collab.choices import STATUS
from collab.choices import STATUS_MODERE
from collab.db_utils import commit_data
from collab.db_utils import create_feature_sql
from collab.db_utils import edit_feature_sql
from collab.views.views import get_anonymous_rights

# from collab.views.project_services import generate_feature_id
from collab.views.project_services import delete_feature
from collab.views.project_services import get_feature
from collab.views.project_services import get_feature_detail
# from collab.views.project_services import get_feature_uuid
from collab.views.project_services import get_project_features
from collab.views.project_services import project_feature_type_fields
from collab.views.project_services import project_features_types

from collab.views.validation_services import diff_data
from collab.views.validation_services import validate_geom

from collections import OrderedDict
import datetime


# from django.db.models import Q
from django.conf import settings
# from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import GEOSGeometry
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.shortcuts import redirect
from django.views import View
from collab.exif import exif

import logging
import os

APP_NAME = __package__.split('.')[0]


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
        table_name = """{app_name}_{project_slug}_{feature_type_slug}""".format(
                        app_name=APP_NAME,
                        project_slug=project_slug,
                        feature_type_slug=feature_type_slug)
        if request.POST.dict().get('_method', '') == 'delete':
            deletion = delete_feature(APP_NAME, project_slug, feature_type_slug, feature_id, request.user)
            if deletion == True:
                return redirect('project_feature_list', project_slug=project_slug)
            else:
                msg = "Une erreur s'est produite, veuillez renouveller votre demande ultérieurement"
                logger = logging.getLogger(__name__)
                logger.exception(deletion)
                request.session['error'] = msg
                return redirect('project_feature_detail', project_slug=project_slug,
                                feature_type_slug=feature_type_slug, feature_id=feature_id)

        project = get_object_or_404(models.Project,
                                    slug=project_slug)
        prev_feature = get_feature(APP_NAME, project_slug, feature_type_slug, feature_id)
        # get user right on project
        data = request.POST.dict()
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
            # log de l'event de modification d'un projet
            data_modify = {}
            curr_feature = get_feature(APP_NAME, project_slug, feature_type_slug, feature_id)
            data_modify = diff_data(prev_feature, curr_feature)
            # data Modify
            models.Event.objects.create(
                user=request.user,
                event_type='update_attrs',
                object_type='feature',
                project_slug=project.slug,
                feature_id=feature_id,
                data=data_modify
            )

            return redirect('project_feature_detail', project_slug=project_slug,
                            feature_type_slug=feature_type_slug, feature_id=feature_id)
        else:
            msg = "Une erreur s'est produite, veuillez renouveller votre demande ultérieurement"
            logger = logging.getLogger(__name__)
            logger.exception(creation)
            request.session['error'] = msg
            return redirect('project_feature_detail', project_slug=project_slug,
                            feature_type_slug=feature_type_slug, feature_id=feature_id)



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
        if request.FILES.get('geo_file', ''):
            geo_file = request.FILES.get('geo_file', '')
            path = default_storage.save('tmp/'+geo_file.name, ContentFile(geo_file.read()))
            real_path = os.path.join(settings.MEDIA_ROOT, path)
            try:
                data_geom_wkt = exif.get_image_geoloc_as_wkt(real_path, with_alt=False, ewkt=False)
            except Exception as e:
                path = default_storage.delete('tmp/'+geo_file.name)
                request.session['error'] = "Votre image n'est géolocalisée"
                return redirect('project_add_feature', project_slug=project_slug)
            path = default_storage.delete('tmp/'+geo_file.name)
            # get geom ( à ameliore si les 2 infos de geometrie sont fournis)
            data.pop('geom', None)
        else:
            # get geom
            data_geom_wkt = data.pop('geom', None)
        geom, msg = validate_geom(data_geom_wkt, feature_type_slug, project)
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
