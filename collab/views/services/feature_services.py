from collab import models
from collab.choices import STATUS
from collab.views.services.validation_services import diff_data
from .project_services import get_feature_type_table_name
from collab.db_utils import commit_data
from collab.db_utils import fetch_first_row
from collab.db_utils import fetch_raw_data
from collab import models
from collections import OrderedDict
import dateutil.parser
from django.utils import timezone
import re

from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from hashlib import md5
import logging


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
    logger = logging.getLogger(__name__)
    logger.exception(deletion)
    # attachment
    models.Attachment.objects.filter(feature_type_slug=feature_type_slug).delete()
    # comments
    models.Comment.objects.filter(feature_type_slug=feature_type_slug).delete()
    # delete events
    models.Event.objects.filter(feature_type_slug=feature_type_slug).delete()
    # delete type of feature
    models.FeatureType.objects.filter(feature_type_slug=feature_type_slug).delete()
    # delete subscription
    models.Subscription.objects.filter(feature_type_slug=feature_type_slug).delete()
    return deletion


def archive_all_features(app_name, project_slug, feature_type, archive_date=None):
    """
        Archive all feature regarding a specific date if given
        @param app_name name of the application
        @param project_slug project slug
        @param feature_type type of the feature
        @param archive_date archive date for a given project
        @param user user
    """
    table_name = get_feature_type_table_name(app_name, project_slug, feature_type)
    # liste ids to archive
    sql = """ UPDATE {table_name}
              SET status='3'
              WHERE archive_date < '{archive_date}';
          """.format(table_name=table_name, archive_date=archive_date)
    modification = commit_data('default', sql)
    return modification


def delete_all_features(app_name, project_slug, feature_type, deletion_date=None):
    """
        Delete all feature regarding a specific date if given
        @param app_name name of the application
        @param project_slug project slug
        @param feature_type type of the feature
        @param deletion_date deletion date for a given project
        @param user user
    """
    table_name = get_feature_type_table_name(app_name, project_slug, feature_type)
    # liste ids to delete
    sql = """ SELECT feature_id::varchar,title
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
        # delete events
        models.Event.objects.filter(feature_id__in=list_ids).delete()
        # delete subscription
        models.Subscription.objects.filter(feature_id__in=list_ids).delete()
        return deletion
    return data


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
    # delete events
    models.Event.objects.filter(feature_id=feature_id).delete()
    # delete subscription
    models.Subscription.objects.filter(feature_id=feature_id).delete()
    # à voir si il faut logger cette evenement
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


def feature_update_events(curr_feature, prev_feature, project, user, feature_type_slug, feature_id):
    """
        Create events when a feature is updated
        @param curr_feature feature  after update
        @param prev_feature feature before update
        @param project  project
        @param user user at the origine of the feature update
        @param feature_type_slug feature slug
        @param feature_id id of the modify fetaure
        @return
    """

    data_modify = {}
    curr_feature.pop('modification_date', 'None')
    prev_feature.pop('modification_date', 'None')
    # log modification of geometrie
    if 'geom' in curr_feature.keys():
        if prev_feature['geom'] != curr_feature['geom']:
            # status Modify
            models.Event.objects.create(
                user=user,
                event_type='update_loc',
                object_type='feature',
                project_slug=project.slug,
                feature_type_slug=feature_type_slug,
                feature_id=feature_id,
                data={
                    'key': str(feature_id),
                    'previous_value': prev_feature['geom'],
                    'current_value': curr_feature['geom']})
            # remove status from dict
            prev_feature.pop('geom', 'None')
            curr_feature.pop('geom', 'None')
    # log modification of status
    if 'status' in curr_feature.keys():
        if prev_feature['status'] != curr_feature['status']:
            # status Modify
            models.Event.objects.create(
                user=user,
                event_type='update_status',
                object_type='feature',
                project_slug=project.slug,
                feature_type_slug=feature_type_slug,
                feature_id=feature_id,
                data={
                    'key': str(feature_id),
                    'previous_value': STATUS[int(prev_feature['status'])][1],
                    'current_value': STATUS[int(curr_feature['status'])][1]})
            # remove status from dict
            prev_feature.pop('status', 'None')
            curr_feature.pop('status', 'None')
    # data Modify
    data_modify = diff_data(prev_feature, curr_feature)
    if data_modify:
        models.Event.objects.create(
            user=user,
            event_type='update_attrs',
            object_type='feature',
            project_slug=project.slug,
            feature_type_slug=feature_type_slug,
            feature_id=feature_id,
            data=data_modify)


def edit_feature_sql(data):
    """
        Get sql for the modification of a feature
    """
    # remove the csrfmiddlewaretoken key
    data.pop('csrfmiddlewaretoken', None)
    data.pop('feature', None)
    add_sql = ""
    date_pattern = re.compile('^[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4}$')
    # replace 'on' by 'true'
    for key, val in data.items():
        if not val:
            add_sql += """,{key}=NULL""".format(
                       key=str(key))
        elif date_pattern.match(str(val)):
            format_date = timezone.make_aware(dateutil.parser.parse(val), timezone.get_current_timezone())
            add_sql += """,{key}='{format_date}'""".format(
                           key=str(key),
                           format_date=str(format_date))
        elif val == "on":
            add_sql += """,{key}={val}""".format(
                    key=str(key),
                    val=True)
        else:
            add_sql += """,{key}='{val}'""".format(
                    key=str(key),
                    val=str(val))

    return add_sql


def create_feature_sql(data):
    """
        Get sql for the creation of a feature
     """
    # remove the csrfmiddlewaretoken key
    data.pop('csrfmiddlewaretoken', None)
    data.pop('feature', None)
    # replace 'on' by 'true'
    for key, val in data.items():
        if val == "on":
            data[key] = 'True'
    # remove empty keys -> A AMELIORER "'" !!!!!!!!!
    data = {k: v for k, v in data.items() if v}
    data_keys = " "
    data_values = " "
    if data.keys():
        data_keys = ' , ' + ' , '.join(list(data.keys()))
    if data.values():
        data_values = " , '" + "' , '".join(list(data.values())) + "'"

    return data_keys, data_values


def get_feature_event(feature_id, nb_event=3):
    """
        Get all the event which append on a feature
        @param feature_id id of the feature
        @param nb_event number of event
        @return events
    """

    events = models.Event.objects.filter(feature_id=feature_id).order_by('-creation_date')
    if len(events) > nb_event:
        return events[0:nb_event]
    else:
        return events
