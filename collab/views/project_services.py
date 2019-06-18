from collab.choices import STATUS
from collab.db_utils import commit_data
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


def get_feature_type_table_prefix(app_name, project_slug):
    return "{app_name}_{project_slug}".format(app_name=app_name, project_slug=project_slug)


def get_feature_type_table_name(app_name, project_slug, feature_type):
    feature_type_table_prefix = get_feature_type_table_prefix(app_name, project_slug)
    return "{feature_type_table_prefix}_{feature_type}".format(
        feature_type_table_prefix=feature_type_table_prefix, feature_type=feature_type)


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
    feature_type_table_prefix = get_feature_type_table_prefix(app_name, project_slug)
    sql = """ SELECT  table_name
            FROM information_schema.tables
            WHERE table_type='BASE TABLE'
            AND table_schema='public' AND table_name LIKE '{feature_type_table_prefix}%';
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
    sql = """ SELECT *
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


def get_feature(app_name, project_slug, feature_type, feature_id):
    """
        Return a specific feature
        @param app_name name of the application
        @param project_slug project slug
        @param feature_type type of the feature
        @param id id of the feature
        @return JSON
    """
    table_name = get_feature_type_table_name(app_name, project_slug, feature_type)
    sql = """ SELECT *
              FROM "{table_name}"
              WHERE feature_id='{feature_id}';
          """.format(table_name=table_name, feature_id=feature_id)
    data = fetch_first_row('default', sql)
    return OrderedDict(sorted(data.items()))


def get_feature_detail(app_name, project_slug, feature_type, feature_id):
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
    feature = get_feature(app_name, project_slug, feature_type, feature_id)
    if feature.get('status', ''):
        feature['status'] = STATUS[int(feature['status'])][1]
    if feature.get('user_id', ''):
        try:
            user = models.CustomUser.objects.get(
                                     id=feature['user_id'])
        except Exception as e:
            user = 'Anonyme'
    return project, feature, user


def get_feature_pk(table_name, feature_id):
    """
        Return the pk of a specific feature
        @param table_name table name
        @param feature_id uuid of the feature
        @return JSON
    """

    sql = """ SELECT feature_id AS pk
              FROM "{table_name}"
              WHERE feature_id='{feature_id}';
          """.format(table_name=table_name, feature_id=feature_id)
    data = fetch_first_row('default', sql)
    return data.get('pk', '')


def get_feature_uuid(table_name, feature_pk):
    """
        Return the pk of a specific feature
        @param table_name table name
        @param feature_pk pk of the feature
        @return feature_id uuid of the feature
    """

    sql = """ SELECT feature_id
              FROM "{table_name}"
              WHERE id='{id}';
          """.format(table_name=table_name, id=id)
    data = fetch_first_row('default', sql)
    return data.get('feature_id', '')


def delete_feature(app_name, project_slug, feature_type, feature_id, user):
    """
        Delete a specific feature and link data
        @param app_name name of the application
        @param project_slug project slug
        @param feature_type type of the feature
        @param feature_id uuid of the feature
        @param user user
    """
    table_name = get_feature_type_table_name(app_name, project_slug, feature_type)
    sql = """ DELETE
              FROM "{table_name}"
              WHERE feature_id='{feature_id}';
          """.format(table_name=table_name, feature_id=feature_id)
    deletion = commit_data('default', sql)

    # attachment
    models.Attachment.objects.filter(feature_id=feature_id).delete()
    # comments
    models.Comment.objects.filter(feature_id=feature_id).delete()
    models.Event.objects.create(
        user=user,
        event_type='delete',
        object_type='feature',
        project_slug=project_slug,
        feature_id=feature_id,
        feature_type_slug=feature_type,
        data={}
    )
    return deletion
