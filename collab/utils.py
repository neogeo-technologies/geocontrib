from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def handle_email(users, context):

    subject = 'Message de notification.'
    try:
        from_email = settings.DEFAULT_FROM_EMAIL
    except:
        from_email = "ne-pas-repondre@collab.fr"

    for user in users:

        context["user"] = user
        html_message = render_to_string(
            'collab/notification.html',
            context=context
        )
        plain_message = strip_tags(html_message)

        mail.send_mail(
            subject, plain_message, from_email,
            recipient_list=[user.email, ], html_message=html_message)
