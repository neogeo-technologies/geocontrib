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

import logging
logger = logging.getLogger(__name__)

User = get_user_model()


class Command(BaseCommand):
    help = """Commande pouvant etre associé à une tache CRON et notifiant les utilisateurs,
        des publications de document clé dans les projets auxquelles ils sont abonnés."""

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

        for user in users:
            # Process each user for their subscriptions and pending notifications
            project_slugs = Subscription.objects.filter(
                users=user
            ).values_list('project__slug', flat=True)

            for slug in project_slugs:
                # Filter only key document published events
                pending_stack = StackedEvent.objects.filter(
                    project_slug=slug, state='pending',
                    schedualed_delivery_on__lte=now(),
                    only_key_document=True
                )

                # If there are pending notifications, serialize and prepare them
                if pending_stack.exists():
                    serialized_project = ProjectDetailedSerializer(Project.objects.get(slug=slug))
                    # On ne peut avoir qu'une pile en attente pour un projet donnée
                    serialized_stack = StackedEventSerializer(pending_stack.first())

                    for event in serialized_stack.data.get('events'):
                        # Send a notification for each event individually
                        context = {
                            'project_name': serialized_project.data['title'],
                            'events_data': [event],
                        }
                        try:
                            notif_suscriber_key_documents(emails=[user.email, ], context=context)
                        except Exception:
                            logger.exception('Error on notif_suscriber_key_documents: {0}'.format(user.email))
                        else:
                            logger.info('Notification sent to {0}'.format(user.email))

        # TODO @cbenhabib: revoir la gestion des stack en erreur
        for row in StackedEvent.objects.filter(state='pending', schedualed_delivery_on__lte=now(), only_key_document=True):
            row.state = 'successful'
            row.save()

        logger.info('Command succeeded! ')
