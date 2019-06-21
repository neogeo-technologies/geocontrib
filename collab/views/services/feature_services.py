from collab.choices import STATUS
from .project_services import get_feature_type_table_name
from collab.db_utils import commit_data
from collab.db_utils import fetch_first_row
from collab.db_utils import fetch_raw_data
from collab import models
from collections import OrderedDict
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.crypto import get_random_string
from hashlib import md5


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


def delete_feature_table(app_name, project_slug, feature_type_slug):
    """
        Delete a specific table
        @param app_name name of the application
        @param project_slug project slug
        @param feature_type_slug type of the feature
        @return JSON
    """
    table_name = get_feature_type_table_name(app_name, project_slug, feature_type_slug)
    # liste ids to delete
    sql = """ DROP TABLE "{table_name}";
          """.format(table_name=table_name)
    deletion = commit_data('default', sql)
    return deletion


def delete_all_features(app_name, project_slug, feature_type, deletion_date=None):
    """
        Delete all feature regardiing a specific date if given
        @param app_name name of the application
        @param project_slug project slug
        @param feature_type type of the feature
        @param deletion_date deletion date for a given project
        @param user user
    """
    table_name = get_feature_type_table_name(app_name, project_slug, feature_type)
    # liste ids to delete
    sql = """ SELECT feature_id
              FROM "{table_name}"
              WHERE deletion_date < '{deletion_date}';
          """.format(table_name=table_name, deletion_date=deletion_date)
    data = fetch_raw_data('default', sql)
    list_ids = []
    if data:
        list_ids = [d['feature_id'] for d in data]
        # deletion
        sql = """ DELETE
                  FROM "{table_name}"
                  WHERE deletion_date < '{deletion_date}';
              """.format(table_name=table_name, deletion_date=deletion_date)
        deletion = commit_data('default', sql)
        # attachment
        models.Attachment.objects.filter(feature_id__in=list_ids).delete()
        # comments
        models.Comment.objects.filter(feature_id__in=list_ids).delete()
    return list_ids


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
    # à voir si il faut logger cette evenement
    # models.Event.objects.create(
    #     user=user,
    #     event_type='delete',
    #     object_type='feature',
    #     project_slug=project_slug,
    #     feature_id=feature_id,
    #     feature_type_slug=feature_type,
    #     data={}
    # )
    return deletion


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
    sql = """ SELECT *, ST_AsGeoJSON(geom) as geom
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
