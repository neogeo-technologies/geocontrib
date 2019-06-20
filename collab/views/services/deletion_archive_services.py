from .project_services import get_feature_type_table_name
from collab.db_utils import commit_data
from collab.db_utils import fetch_raw_data
from collab import models


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
