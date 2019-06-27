from collab.db_utils import fetch_first_row
from collab.db_utils import fetch_raw_data
from collab import models
from collections import OrderedDict
from django.core import serializers
from django.http import HttpResponse
# import re


def get_feature_type_table_prefix(app_name, project_slug):
    return "{app_name}_{project_slug}".format(app_name=app_name, project_slug=project_slug)


def get_feature_type_table_name(app_name, project_slug, feature_type):
    feature_type_table_prefix = get_feature_type_table_prefix(app_name, project_slug)
    return "{feature_type_table_prefix}_{feature_type}".format(
        feature_type_table_prefix=feature_type_table_prefix, feature_type=feature_type)


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
    feature_type_table_prefix = get_feature_type_table_prefix(app_name, project_slug)
    sql = """ SELECT  table_name
            FROM information_schema.tables
            WHERE table_type='BASE TABLE'
            AND table_schema='public' AND table_name LIKE '{feature_type_table_prefix}\_%';
          """.format(feature_type_table_prefix=feature_type_table_prefix)
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
    table_name = get_feature_type_table_name(app_name, project_slug, feature_type)
    sql = """ SELECT COUNT(*) FROM "{table_name}" ;
          """.format(table_name=table_name)
    num = fetch_first_row('default', sql)
    return num.get('count', 0)


def project_feature_type_fields(app_name, project_slug, feature_type_slug):
    """
        Type of fields for a given feature type
        @param app_name name of the application
        @param project_slug project slug
        @param feature_type_slug type of the feature
        @return JSON
    """
    table_name = get_feature_type_table_name(app_name, project_slug, feature_type_slug)
    sql = """ SELECT column_name,data_type,udt_name as type,
              character_maximum_length as char_max_size,
              null As info
              from information_schema.columns WHERE table_schema='public'
              AND table_name = '{table_name}';
          """.format(table_name=table_name)
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
    table_name = get_feature_type_table_name(app_name, project_slug, feature_type)
    sql = """ SELECT *,feature_id::varchar, ST_AsGeoJSON(geom) as geom
              FROM "{table_name}"
              ORDER BY creation_date DESC ;
          """.format(table_name=table_name)
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
    table_name = get_feature_type_table_name(app_name, project_slug, feature_type)
    limit = ""
    if num:
        limit = "  LIMIT " + str(num)
    sql = """ SELECT collab_customuser.id AS userid,
              first_name,last_name,"{table_name}".feature_id as pk,
              user_id,feature_id,title,creation_date
              FROM "{table_name}"
              INNER JOIN public.collab_customuser ON
              user_id=collab_customuser.id
              ORDER BY creation_date DESC {limit};
          """.format(table_name=table_name,
                     limit=limit)
    data = fetch_raw_data('default', sql)
    return data
