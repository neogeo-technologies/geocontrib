from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from django.utils.timezone import now

from api.serializers import ProjectDetailedSerializer
from api.serializers import StackedEventSerializer

from geocontrib.emails import notif_suscriber_grouped_events
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
    """
    A Django management command intended to be run as a scheduled task (CRON job).
    This command fetches and sends grouped event notifications to users based on their
    subscription preferences and notification settings.
    """
    help = """Commande pouvant etre associé à une tache CRON et notifiant les utilisateurs,
        des evenements les concernant."""

    def handle(self, *args, **options):
        """
        The entry point for the management command which checks user notification settings
        and sends out emails based on the specified frequency and type.
        """

        # Verify that the frequency setting in settings.py is correctly configured
        frequency_setted = settings.DEFAULT_SENDING_FREQUENCY
        if frequency_setted not in ['instantly', 'daily', 'weekly']:
            logger.error('The default frequency setting is incorrect')
            return

        # Fetch all active users
        users = User.objects.filter(is_active=True)
        # Get the notification model data from the database in order to check if notification_type is per project
        notification_model = NotificationModel.objects.get(
            template_name='Événements groupés'
        )

        # Process each user for their subscriptions and pending notifications
        for user in users:
            # Pour chaque utilisateur on filtre les abonnements projets
            project_slugs = Subscription.objects.filter(
                users=user
            ).values_list('project__slug', flat=True)
            
            stacked_events = []
            context = {}

            # Gather all pending notifications for subscribed projects
            for slug in project_slugs:
                # Filter out key documents events
                pending_stack = StackedEvent.objects.filter(
                    project_slug=slug, state='pending',
                    schedualed_delivery_on__lte=now(),
                    only_key_document=False
                )

                # If there are pending notifications, serialize and prepare them
                if pending_stack.exists():
                    serialized_project = ProjectDetailedSerializer(Project.objects.get(slug=slug))
                    # On ne peut avoir qu'une pile en attente pour un projet donnée
                    serialized_stack = StackedEventSerializer(pending_stack.first())

                    # Check if notifications should be sent per project or globally
                    if notification_model.notification_type == 'per_project':
                        # Send a notification for each project individually
                        single_project_context = {
                            'project_name': serialized_project.data['title'],
                            'stacked_events': [{
                                'project_data': serialized_project.data,
                                'stack_data': serialized_stack.data,
                            }]
                        }
                        try:
                            notif_suscriber_grouped_events(emails=[user.email, ], context=single_project_context)
                        except Exception:
                            logger.exception('Error on notif_suscriber_grouped_events: {0}'.format(user.email))
                        else:
                            logger.info('Batch sent to {0}'.format(user.email))
                    else:
                        # Collect all events for a global notification
                        stacked_events.append(
                            {
                                'project_data': serialized_project.data,
                                'stack_data': serialized_stack.data,
                            }
                        )

            # If global notifications are enabled, send them out
            if notification_model.notification_type == 'global':
                context['stacked_events'] = stacked_events
                if len(context['stacked_events']) > 0:
                    try:
                        notif_suscriber_grouped_events(emails=[user.email, ], context=context)
                    except Exception:
                        logger.exception('Error on notif_suscriber_grouped_events: {0}'.format(user.email))
                    else:
                        logger.info('Batch sent to {0}'.format(user.email))

        # TODO @cbenhabib: revoir la gestion des stack en erreur
        # Update the state of processed notifications
        for row in StackedEvent.objects.filter(state='pending', schedualed_delivery_on__lte=now(), only_key_document=False):
            row.state = 'successful'
            row.save()

        logger.info('Command succeeded!')
