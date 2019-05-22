from collab.choices import STATUS
from collab.db_utils import fetch_first_row
from collab.db_utils import fetch_raw_data
from collab import models
from collections import OrderedDict
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.crypto import get_random_string
from hashlib import md5
# import re


def get_project_feature_geom_type(app_name, project_slug, feature):
    """
        Return the feature geometry for a type of feature
        @app_name name of  the current application
        @project_slug slug of the feature project
        @feature feature name
        @return type of geom
    """

    try:
        project = models.Project.objects.get(slug=project_slug)
        for elt in project.feature_type:
            if elt.get("feature", "") == feature:
                return elt.get('geom_type', "Non défini")
        return "Non défini"
    except Exception as e:
        return "Non défini"


def generate_feature_id(app_name, project_slug, feature):
    """
        Generate a unique uuid for a feature based on
        feature parameters
        @app_name name of  the current application
        @project_slug slug of the feature project
        @feature feature name
        @return unique uuid
    """
    tz = str(timezone.now())
    random = get_random_string(8).lower()
    feature_id = (app_name + project_slug + feature + random + tz).encode('utf-8')
    return md5(feature_id).hexdigest()


def project_list(request):
    """
        List of available projects
        @param
        @return JSON
    """
    qs_json = serializers.serialize('json', models.Project.objects.all())
    return HttpResponse(qs_json, content_type='application/json')


def last_user_registered(project_slug, nbuser=None):
    """
        List of user registered within a project
        @param project_slug project slug
        @param nbuser number of users wanted
        @return JSON
    """
    if nbuser:
        return models.Autorisation.objects.filter(project__slug=project_slug
               ).order_by('creation_date').values('user')[0:nbuser]
    else:
        return models.Autorisation.objects.filter(project__slug=project_slug
               ).order_by('creation_date').values('user__username',
                                                  'user__first_name',
                                                  'user__last_name')


def project_features_types(app_name, project_slug):
    """
        List the feature types for a given project
        @param app_name name of the application
        @param project_slug project slug
        @return JSON
    """
    sql = """ SELECT table_name
            FROM information_schema.tables
            WHERE table_type='BASE TABLE'
            AND table_schema='public' AND table_name LIKE '{app_name}_{slug}%';
          """.format(app_name=app_name, slug=project_slug)
    res = fetch_raw_data('default', sql)
    list_feature = []
    for elt in res:
        # name = re.search('_\w+$', elt.get('table_name', ''))
        try:
            name = elt.get('table_name', '')
            if name:
                list_feature.append(name.split('_')[-1:][0])
        except Exception as e:
            pass
    return list_feature


def project_feature_number(app_name, project_slug, feature_type):
    """
        Return the number of features per project
        @param app_name name of the application
        @param project_slug project slug
        @param feature_type type of the feature
        @return JSON
    """

    sql = """ SELECT COUNT(*) FROM "{app_name}_{slug}_{feature_type}" ;
          """.format(app_name=app_name, slug=project_slug,
                     feature_type=feature_type)
    num = fetch_first_row('default', sql)
    return num.get('count', 0)


def project_feature_type_fields(app_name, project_slug, feature_type):
    """
        Type of fields for a given feature type
        @param app_name name of the application
        @param project_slug project slug
        @param feature_type type of the feature
        @return JSON
    """
    sql = """ SELECT column_name,data_type,udt_name as type,
              character_maximum_length as char_max_size,
              null As info
              from information_schema.columns WHERE table_schema='public'
              AND table_name LIKE '{app_name}_{slug}_{feature_type}%';
          """.format(app_name=app_name, slug=project_slug,
                     feature_type=feature_type)
    data = fetch_raw_data('default', sql)
    res = {}
    for elt in data:
        res[elt['column_name']] = elt
    return res


def get_project_features(app_name, project_slug, feature_type):
    """
        Return the features of a given feature type
        @param app_name name of the application
        @param project_slug project slug
        @param feature_type type of the feature
        @return JSON
    """
    sql = """ SELECT *
              FROM "{app_name}_{slug}_{feature_type}"
              ORDER BY date_creation DESC ;
          """.format(app_name=app_name, slug=project_slug,
                     feature_type=feature_type)
    data = fetch_raw_data('default', sql)

    return [OrderedDict(sorted(v.items())) for v in data]


def get_last_features(app_name, project_slug, feature_type, num=""):
    """
        Return the last features saved for a given feature type
        @param app_name name of the application
        @param project_slug project slug
        @param feature_type type of the feature
        @param num number of features required
        @return JSON
    """
    limit = ""
    if num:
        limit = "  LIMIT " + str(num)
    sql = """ SELECT collab_customuser.id AS userid,
              first_name,last_name,"{app_name}_{slug}_{feature_type}".id as pk,
              user_id,feature_id,titre,date_creation
              FROM "{app_name}_{slug}_{feature_type}"
              INNER JOIN public.collab_customuser ON
              user_id=collab_customuser.id
              ORDER BY date_creation DESC {limit};
          """.format(app_name=app_name, slug=project_slug,
                     feature_type=feature_type,
                     limit=limit)
    data = fetch_raw_data('default', sql)
    return data


def get_feature(app_name, project_slug, feature_type, id):
    """
        Return a specific feature
        @param app_name name of the application
        @param project_slug project slug
        @param feature_type type of the feature
        @param id id of the feature
        @return JSON
    """
    sql = """ SELECT *
              FROM "{app_name}_{slug}_{feature_type}"
              WHERE id={id};
          """.format(app_name=app_name, slug=project_slug,
                     feature_type=feature_type, id=id)
    data = fetch_first_row('default', sql)
    return OrderedDict(sorted(data.items()))


def get_feature_detail(app_name, project_slug, feature_type, feature_pk):
    """
        Return the detail of a specific feature
        @param app_name name of the application
        @param project_slug project slug
        @param feature_type type of the feature
        @param feature_pk pk of the feature
        @return JSON
    """
    # Get project info from slug
    # get project
    project = get_object_or_404(models.Project,
                                slug=project_slug)
    # get features fields
    feature = get_feature(app_name, project_slug, feature_type, feature_pk)
    if feature.get('status', ''):
        feature['status'] = STATUS[int(feature['status'])][1]
    if feature.get('user_id', ''):
        feature['utilisateur'] = feature.pop('user_id')
        try:
            feature['utilisateur'] = models.CustomUser.objects.get(
                                     id=feature['utilisateur'])
        except Exception as e:
            feature['utilisateur'] = 'Anonyme'

    return project, feature
