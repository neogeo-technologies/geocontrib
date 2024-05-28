from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from django.utils.timezone import now

from api.serializers import ProjectDetailedSerializer
from api.serializers import StackedEventSerializer

from geocontrib.emails import notif_suscriber_key_documents
from geocontrib.models import Project
from geocontrib.models import StackedEvent
from geocontrib.models import Subscription
"""
import directly from the file to avoid circular import and not from model/__init__.py
since there are imports into a model(annotation.py) from geocontrib/emails.py
which trigger import of NotificationModel before the model is fully registrated
fixed by removing the import from model/__init__.py
"""
from geocontrib.models.notification import NotificationModel

import logging
logger = logging.getLogger(__name__)

User = get_user_model()


class Command(BaseCommand):
    help = """Commande pouvant etre associé à une tache CRON et notifiant les utilisateurs,
        des publications de document clé dans les projets auxquelles ils sont abonnés."""

    def handle(self, *args, **options):

        frequency_setted = settings.DEFAULT_SENDING_FREQUENCY
        if frequency_setted not in ['instantly', 'daily', 'weekly']:
            logger.error('The default frequency setting is incorrect')
            return

        users = User.objects.filter(is_active=True)
        # Get the template data to check if notification_type is per project
        notification_model = NotificationModel.objects.get(
            template_name='Événements groupés'
        )
        for user in users:

            # Pour chaque utilisateur on filtre les abonnements projets
            project_slugs = Subscription.objects.filter(
                users=user
            ).values_list('project__slug', flat=True)
            stacked_events = []
            context = {}
            for slug in project_slugs:
                # Filter only key document published events
                pending_stack = StackedEvent.objects.filter(
                    project_slug=slug, state='pending',
                    schedualed_delivery_on__lte=now(),
                    only_key_document=True
                )

                if pending_stack.exists():
                    serialized_project = ProjectDetailedSerializer(Project.objects.get(slug=slug))
                    # On ne peut avoir qu'une pile en attente pour un projet donnée
                    serialized_stack = StackedEventSerializer(pending_stack.first())

                    if notification_model.notification_type == 'per_project':
                        # Send email per project
                        single_project_context = {
                            'project_name': serialized_project.data['title'],
                            'stacked_events': [{
                                'project_data': serialized_project.data,
                                'stack_data': serialized_stack.data,
                            }]
                        }
                        try:
                            notif_suscriber_key_documents(emails=[user.email, ], context=single_project_context)
                        except Exception:
                            logger.exception('Error on notif_suscriber_key_documents: {0}'.format(user.email))
                        else:
                            logger.info('Batch sent to {0}'.format(user.email))
                    else:    
                        stacked_events.append(
                            {
                                'project_data': serialized_project.data,
                                'stack_data': serialized_stack.data,
                            }
                        )
            if notification_model.notification_type == 'global':
                context['stacked_events'] = stacked_events
                if len(context['stacked_events']) > 0:
                    try:
                        notif_suscriber_key_documents(emails=[user.email, ], context=context)
                    except Exception:
                        logger.exception('Error on notif_suscriber_key_documents: {0}'.format(user.email))
                    else:
                        logger.info('Batch sent to {0}'.format(user.email))

        # TODO @cbenhabib: revoir la gestion des stack en erreur
        for row in StackedEvent.objects.filter(state='pending', schedualed_delivery_on__lte=now(), only_key_document=True):
            row.state = 'successful'
            row.save()

        logger.info('Command succeeded! ')
