from urllib.parse import urljoin
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.template import Context
from django.template import Template
from django.utils.html import strip_tags

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
    feature = context['feature']

    context['url_feature'] = urljoin(BASE_URL, feature.get_absolute_url())

    subject = "[GéoContrib:{project_slug}] Un signalement est en attente de publication.".format(
        project_slug=feature.project.slug
    )
    email = EmailBaseBuilder(
        context=context, bcc=emails, subject=subject,
        template='geocontrib/email/notif_moderators_pending_features.html')

    email.send()


def notif_creator_published_feature(emails, context):
    feature = context['feature']

    context['url_feature'] = urljoin(BASE_URL, feature.get_view_url())

    subject = "[GéoContrib:{project_slug}] Confirmation de la publication de l'un de vos signalements.".format(
        project_slug=feature.project.slug
    )

    email = EmailBaseBuilder(
        context=context, to=emails, subject=subject,
        template='geocontrib/email/notif_creator_published_feature.html')

    email.send()


def notif_suscriber_grouped_events(emails, context):

    notification_model = NotificationModel.objects.get(template_name="grouped_events")
    if notification_model:
        subject = notification_model.subject

        if notification_model.notification_type == per_project and context.project:
            data = Context({
                'nom_projet': context.project
            })
            template = Template(notification_model.message)
            message = template.render(data)
        else :
            message = notification_model.message

        context['message'] = message

    else:
        subject = "[{}] Activité des projets que vous suivez"

    subject.format(settings.APPLICATION_NAME)
    context['APPLICATION_NAME'] = settings.APPLICATION_NAME

    email = EmailBaseBuilder(
        context=context, to=emails, subject=subject,
        template='geocontrib/email/notif_suscriber_grouped_events.html')

    email.send()
