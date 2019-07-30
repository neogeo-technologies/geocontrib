from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def notif_moderators_pending_features(emails, context):
    feature = context['feature']
    subject = "[Collab:{project_slug}] Un signalement est en attente de publication.".format(
        project_slug=feature.project.slug
    )
    to_emails = emails

    html_message = render_to_string(
        'collab/email/notif_moderators_pending_features.html',
        context=context
    )
    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
        subject, plain_message, from_email=settings.DEFAULT_FROM_EMAIL, bcc=to_emails
    )

    email.attach_alternative(html_message, "text/html")

    email.send()


def notif_suscribers_project_event(emails, context):

    project = context['project']
    subject = "[Collab:{project_slug}] Un projet a été mis à jour.".format(
        project_slug=project.slug
    )
    to_emails = emails

    html_message = render_to_string(
        'collab/email/notif_suscribers_project_event.html',
        context=context
    )
    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
        subject, plain_message, from_email=settings.DEFAULT_FROM_EMAIL, bcc=to_emails
    )

    email.attach_alternative(html_message, "text/html")

    email.send()


def notif_creator_published_feature(emails, context):
    feature = context['feature']
    subject = "[Collab:{project_slug}] Confirmation de la publication de l'un de vos signalement.".format(
        project_slug=feature.project.slug
    )
    to_emails = emails

    html_message = render_to_string(
        'collab/email/notif_creator_published_feature.html',
        context=context
    )
    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
        subject, plain_message, from_email=settings.DEFAULT_FROM_EMAIL, bcc=to_emails
    )

    email.attach_alternative(html_message, "text/html")

    email.send()
