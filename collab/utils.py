from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def handle_email(user, context):

    subject = 'Message de notification.'
    try:
        from_email = settings.DEFAULT_FROM_EMAIL
    except Exception:
        from_email = "ne-pas-repondre@collab.fr"

    # for user in users:
    context["user"] = user
    html_message = render_to_string(
        'collab/notify.html',
        context=context
    )
    plain_message = strip_tags(html_message)

    mail.send_mail(subject=subject,
                   message=plain_message,
                   from_email=from_email,
                   recipient_list=[user.email, ],
                   fail_silently=False)
