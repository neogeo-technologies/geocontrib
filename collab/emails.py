from urllib.parse import urljoin
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.models import Site

import logging
logger = logging.getLogger('django')

try:
    CURRENT_SITE_DOMAIN = Site.objects.get_current().domain
except Exception:
    CURRENT_SITE_DOMAIN = 'http://SETUP-URL-IN-ADMIN'
    logger.error('Sites not migrated yet. Please make sure you have Sites setup on Django Admin')


class EmailBaseBuilder(object):

    def __init__(self, context={}, to=[], bcc=[], subject='', template='', *args, **kwargs):
        self.context = context
        self.to = to
        self.bcc = bcc
        self.subject = subject
        self.template = template
        super().__init__(*args, **kwargs)

    def send(self):
        html_message = render_to_string(
            self.template,
            context=self.context
        )
        plain_message = strip_tags(html_message)

        email = EmailMultiAlternatives(
            self.subject, plain_message, from_email=settings.DEFAULT_FROM_EMAIL,
            to=self.to, bcc=self.bcc
        )

        email.attach_alternative(html_message, "text/html")

        email.send()


def notif_moderators_pending_features(emails, context):
    feature = context['feature']

    context['url_feature'] = urljoin(CURRENT_SITE_DOMAIN, feature.get_absolute_url())

    subject = "[Collab:{project_slug}] Un signalement est en attente de publication.".format(
        project_slug=feature.project.slug
    )
    email = EmailBaseBuilder(
        context=context, bcc=emails, subject=subject,
        template='collab/email/notif_moderators_pending_features.html')

    email.send()


def notif_suscribers_project_event(emails, context):

    project = context['project']
    subject = "[Collab:{project_slug}] Un projet a été mis à jour.".format(
        project_slug=project.slug
    )

    email = EmailBaseBuilder(
        context=context, bcc=emails, subject=subject,
        template='collab/email/notif_suscribers_project_event.html')

    email.send()


def notif_creator_published_feature(emails, context):
    feature = context['feature']

    context['url_feature'] = urljoin(CURRENT_SITE_DOMAIN, feature.get_view_url())

    subject = "[Collab:{project_slug}] Confirmation de la publication de l'un de vos signalement.".format(
        project_slug=feature.project.slug
    )

    email = EmailBaseBuilder(
        context=context, to=emails, subject=subject,
        template='collab/email/notif_creator_published_feature.html')

    email.send()


def notif_suscriber_grouped_events(emails, context):

    subject = "[{}] Activité des projets que vous suivez".format(settings.APPLICATION_NAME)
    context['APPLICATION_NAME'] = settings.APPLICATION_NAME

    email = EmailBaseBuilder(
        context=context, to=emails, subject=subject,
        template='collab/email/notif_suscriber_grouped_events.html')

    email.send()
