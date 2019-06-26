from collab import models
from collab.utils import handle_email
import datetime
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """ Cette fonction permet d'envoyer un mail aux utilisateurs qui sont
               abonnés aux notifications sur un signalement """

    def handle(self, *args, **options):
        for user in models.CustomUser.objects.all():
            res_events = {}
            # get users Subscription
            for subscription in user.subscription_set.all():
                date = datetime.datetime.now().date()
                # get features events
                events = models.Event.objects.filter(feature_id=subscription.feature_id,
                                                     creation_date__contains=date)
                res_events[str(subscription.feature_id)] = { "project": subscription.project_slug,
                                                             "identifiant": str(subscription.feature_id),
                                                             "url": """{domain}projet/{project_slug}/{feature_type}/{feature_id}""".format(
                                                                    domain=settings.BASE_URL,
                                                                    project_slug=subscription.project_slug,
                                                                    feature_type=subscription.feature_type_slug,
                                                                    feature_id=str(subscription.feature_id))}
                # create template
                list_event = []
                for event in events:
                    list_event.append({
                                        "object_type": event.get_object_type_display(),
                                        "event_type": event.get_event_type_display(),
                                        "creation_date": event.creation_date.strftime('%d-%m-%Y %H:%M:%S')})
                res_events[str(subscription.feature_id)].update({'events':list_event})
            # send email to user
            if res_events:
                context = {'first_name': user.first_name,
                           'last_name': user.last_name,
                           'username': user.username,
                           'res': res_events}
                handle_email(user, context)
        self.stdout.write(self.style.SUCCESS('FIN DE L ENVOI DE MAIL.'))
