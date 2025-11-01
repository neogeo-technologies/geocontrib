import sys
import logging
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.contrib.auth import get_user_model

from geocontrib.models import Authorization
from geocontrib.models import Project
from geocontrib.models import Subscription
from geocontrib.emails import notify_project_creation_with_subscription
from geocontrib.utils import generate_subscribe_token
from geocontrib.utils import build_absolute_url

User = get_user_model()
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Notify all project members with email + token subscription link"

    def add_arguments(self, parser):
        parser.add_argument('project_id', type=int)
        parser.add_argument('user_id', type=int)

    def handle(self, *args, **options):
        project = Project.objects.get(pk=options['project_id'])
        sender = User.objects.get(pk=options['user_id'])
        # Log informatif pour tracer si la commande a été déclenché manuellement et non par celery
        if any("manage.py" in arg for arg in sys.argv):
            logger.warning(f"Notification for project {project.title} (slug={project.slug}) manually triggered from shell by user {sender.username} (id={sender.id})")
        # Récupère uniquement les membres du projet avec un rang > 1 (au moins contributeur)
        authorizations = Authorization.objects.filter(
            project=project,
            level__rank__gt=1
        ).select_related('user')
        # Construction de l'URL du projet
        project_url = build_absolute_url(f"projet/{project.slug}")
        # Pour chaque autorisation de membre du projet
        for auth in authorizations:
            # On récupère l'utilisateur associé
            member = auth.user
            # On ne notifie pas celui qui déclenche  
            if member == sender:
                continue 
            # Génération d'un token contenant l'identifiant de l'utilisateur et du projet
            token = generate_subscribe_token(member, project)
            # Construction de l'url pour s'abonner au projet en un clic
            subscribe_url = build_absolute_url(f"subscribe-confirm?token={token}")
            # Envoi de la notification à l'utilisateur
            notify_project_creation_with_subscription(member, project, subscribe_url, project_url)
        # Ajout de la date d'envoi et son auteur dans le projet
        project.notified_members_at = now()
        project.notified_members_by = sender
        project.save()
