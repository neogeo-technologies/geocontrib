from collab import models
from collab.db_utils import fetch_raw_data
from collab.views.services.project_services import get_feature_type_table_name
from collab.views.services.project_services import project_features_types


def get_user_subscriptions(user):
    """
        List of user subscription's
        @param user user
        @return list of features ids
    """
    list_ids = []
    return list_ids


def get_last_user_registered(project_slug, nbuser=None):
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

def get_last_user_comments(user, nbcom=None):
    """
        List of the last user comment's
        @param user user
        @param nbcom number of comments wanted
        @return JSON
    """
    if nbcom:
        return models.Comment.objects.filter(author=user
                   ).order_by('creation_date')[0:nbcom]
    else:
        return models.Comment.objects.filter(author=user
                   ).order_by('creation_date')


def get_last_user_feature(user, app_name, project_slug, feature_type):
    """
        List of the last user features's
        @param table_name table name
        @param user user
        @return JSON
    """
    table_name = get_feature_type_table_name(app_name, project_slug, feature_type)
    sql = """ SELECT DISTINCT *
              FROM {table_name} WHERE user_id='{user_id}';
          """.format(table_name=table_name, user_id=user.id)
    data = fetch_raw_data('default', sql)
    if data:
        for elt in data:
            elt['project'] = project_slug
            elt['feature_type'] = feature_type
        return data[0]
    else:
        return ""


def get_user_feature(app_name, user):
    projects = models.Autorisation.objects.filter(user=user).values('project__slug')
    tables_names = []
    for elt in projects:
        for feature_type in project_features_types(app_name, elt['project__slug']):
            tables_names.append({'table_name': """{app_name}_{project_slug}_{feature_type}""".format(
                                  app_name=app_name,
                                  project_slug=elt['project__slug'],
                                  feature_type=feature_type),
                                  'feature_type': feature_type,
                                  'project': elt['project__slug']})

    return tables_names
