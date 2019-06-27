from collab import models
from collab.db_utils import fetch_raw_data
from collab.views.services.project_services import get_feature_type_table_name
from collab.views.services.project_services import project_features_types


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
    comments = models.Comment.objects.filter(author=user
               ).order_by('-creation_date')
    if comments.count() > nbcom:
        return comments[0:nbcom]
    else:
        return comments


def get_last_user_feature(user, app_name, project_slug, feature_type_slug):
    """
        List of the last user features's
        @param table_name table name
        @param user user
        @return JSON
    """
    table_name = get_feature_type_table_name(app_name, project_slug, feature_type_slug)
    sql = """ SELECT DISTINCT *, feature_id::varchar
              FROM "{table_name}" WHERE user_id='{user_id}';
          """.format(table_name=table_name, user_id=user.id)
    data = fetch_raw_data('default', sql)
    if data:
        for elt in data:
            elt['project'] = project_slug
            elt['feature_type_slug'] = feature_type_slug
        return data[0]
    else:
        return ""


def get_last_user_events(user, nbevents=None):
    """
        List of the last user comment's
        @param user user
        @param nbevents number of events wanted
        @return JSON
    """
    events = []
    for subscription in user.subscription_set.all():
        events.extend(list(models.Event.objects.filter(feature_id=subscription.feature_id)))
    if events:
        sorted_events = sorted(events, key = lambda x: x.creation_date, reverse=True)
        if len(sorted_events) > nbevents:
            return sorted_events[0:nbevents]
        else:
            return sorted_events
    else:
        return events
