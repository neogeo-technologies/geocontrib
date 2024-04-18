from urllib.parse import urljoin
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.template import Context
from django.template import Template
from django.utils.html import strip_tags
"""
import directly from the file to avoid circular import and not from model/__init__.py
since there are imports into a model(annotation.py) from geocontrib/emails.py
which trigger import of NotificationModel before the model is fully registrated
fixed by removing the import from model/__init__.py
"""
from geocontrib.models.mail import NotificationModel

import logging
logger = logging.getLogger(__name__)


BASE_URL = getattr(settings, 'BASE_URL', '')


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
    """
    Get the template elements from the bdd if existing,
    else use the template as it was before storing its object and body header in bdd
    """
    feature = context['feature']

    context['url_feature'] = urljoin(BASE_URL, feature.get_absolute_url())

    notification_model = NotificationModel.objects.get(template_name="Signalement à modérer")
    if notification_model:
        # init context instance to render template & retrieve project_name from context
        data = Context({
            'application_name': settings.APPLICATION_NAME,
            'event_initiator': context['event_initiator'],
            'project_slug': feature.project.slug,
            'project_name': feature.project.title,
            'feature': feature
        })
        # get and render the mail object template
        subject_template = Template(notification_model.subject)
        subject = subject_template.render(data)
        # get the mail body header template
        message_template = Template(notification_model.message)
        # render the mail body header
        message = message_template.render(data)
        # fill context used in EmailBaseBuilder
        context['message'] = message
    else:
        subject = "[GéoContrib:{project_slug}] Un signalement est en attente de publication.".format(
            project_slug=feature.project.slug
        )

    email = EmailBaseBuilder(
        context=context, bcc=emails, subject=subject,
        template='geocontrib/email/notif_moderators_pending_features.html')

    email.send()


def notif_creator_published_feature(emails, context):
    """
    Get the template elements from the bdd if existing,
    else use the template as it was before storing its object and body header in bdd
    """
    feature = context['feature']

    context['url_feature'] = urljoin(BASE_URL, feature.get_view_url())

    notification_model = NotificationModel.objects.get(template_name="Signalement publié")
    if notification_model:
        # init context instance to render template & retrieve project_name from context
        data = Context({
            'application_name': settings.APPLICATION_NAME,
            'url_feature': context['url_feature'],
            'event': context['event'],
            'project_slug': feature.project.slug,
            'project_name': feature.project.title,
            'feature': feature
        })
        # get and render the mail object template
        subject_template = Template(notification_model.subject)
        subject = subject_template.render(data)
        # get the mail body header template
        message_template = Template(notification_model.message)
        # render the mail body header
        message = message_template.render(data)
        # fill context used in EmailBaseBuilder
        context['message'] = message
    else:
        subject = "[GéoContrib:{project_slug}] Confirmation de la publication de l'un de vos signalements.".format(
            project_slug=feature.project.slug
        )

    email = EmailBaseBuilder(
        context=context, to=emails, subject=subject,
        template='geocontrib/email/notif_creator_published_feature.html')

    email.send()


def notif_suscriber_grouped_events(emails, context):
    """
    Get the template elements from the bdd if existing,
    else use the template as it was before storing its object and body header in bdd
    """
    notification_model = NotificationModel.objects.get(template_name="Événements groupés")
    if notification_model:
        # init context instance to render template
        data = Context({
            'application_name': settings.APPLICATION_NAME
        })
        # get and render the mail object template
        subject_template = Template(notification_model.subject)
        subject = subject_template.render(data)

        # get the mail body header template
        message_template = Template(notification_model.message)
        # retrieve project_name from context if notification set to be per project
        if 'project' in context:
            data = Context({    
                'project_name': context.project
            })
        # render the mail body header
        message = message_template.render(data)
        # fill context used in EmailBaseBuilder
        context['message'] = message

    else:
        subject = "[{}] Activité des projets que vous suivez".format(settings.APPLICATION_NAME)

    context['APPLICATION_NAME'] = settings.APPLICATION_NAME

    email = EmailBaseBuilder(
        context=context, to=emails, subject=subject,
        template='geocontrib/email/notif_suscriber_grouped_events.html')

    email.send()
