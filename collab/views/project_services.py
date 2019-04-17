from collab.db_utils import fetch_raw_data
from collab import models
from django.core import serializers
from django.http import HttpResponse
from django.utils import timezone
from django.utils.crypto import get_random_string
from hashlib import md5
import re


def generate_feature_id(app_name, project_slug, feature):
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
        name = re.search('_\w+$', elt.get('table_name', ''))
        if name:
            list_feature.append(name.group(0)[1:])
    return list_feature


def project_features_fields(app_name, project_slug, feature_name):
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
