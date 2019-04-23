from collab.db_utils import fetch_first_row
from collab.db_utils import fetch_raw_data
from collab import models
from django.core import serializers
from django.http import HttpResponse
from django.utils import timezone
from django.utils.crypto import get_random_string
from hashlib import md5
import re


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
        List of projects availables
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
        Type of features available for a given project
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


def project_feature_number(app_name, project_slug, feature_name):
    """
        Return the number of feature per project
        @param app_name name of the application
        @param project_slug project slug
        @param feature_name name of the feature
        @return JSON
    """

    sql = """ SELECT COUNT(*) FROM "{app_name}_{slug}_{feature_name}" ;
          """.format(app_name=app_name, slug=project_slug,
                     feature_name=feature_name)
    num = fetch_first_row('default', sql)
    return num.get('count', 0)


def project_feature_fields(app_name, project_slug, feature_name):
    """
        Type of fields for a given feature
        @param app_name name of the application
        @param project_slug project slug
        @param feature_name name of the feature
        @return JSON
    """
    sql = """ SELECT column_name,data_type,udt_name as type,
              character_maximum_length as char_max_size,
              null As info
              from information_schema.columns WHERE table_schema='public'
              AND table_name LIKE '{app_name}_{slug}_{feature_name}%';
          """.format(app_name=app_name, slug=project_slug,
                     feature_name=feature_name)
    data = fetch_raw_data('default', sql)
    res = {}
    for elt in data:
        res[elt['column_name']] = elt
    return res


def get_project_features(app_name, project_slug, feature_name):
    """
        Return the features of a given project
        @param app_name name of the application
        @param project_slug project slug
        @param feature_name name of the feature
        @return JSON
    """
    sql = """ SELECT *
              FROM "{app_name}_{slug}_{feature_name}" ORDER BY
              date_creation DESC ;
          """.format(app_name=app_name, slug=project_slug,
                     feature_name=feature_name)
    data = fetch_raw_data('default', sql)
    return data


def get_last_features(app_name, project_slug, feature_name, num=""):
    """
        Return the last features saved
        @param app_name name of the application
        @param project_slug project slug
        @param feature_name name of the feature
        @param num number of features required
        @return JSON
    """
    limit = ""
    if num:
        limit = "  LIMIT " + str(num)

    sql = """ SELECT id,feature_id,titre
              FROM "{app_name}_{slug}_{feature_name}" ORDER BY
              date_creation DESC {limit};
          """.format(app_name=app_name, slug=project_slug,
                     feature_name=feature_name,
                     limit=limit)
    data = fetch_raw_data('default', sql)
    return data