import os
import django
import argparse
import logging
from django.core.mail import send_mail


"""
Script d'envoi de mails pour Geocontrib

Contexte :
---------
Afin de simplifier le débogage des e-mails, y compris dans des situations non standard, 
ce script a été créé pour envoyer des e-mails de la même manière que Geocontrib. 
Il utilise les mêmes configurations et envoie via les mêmes outils, tout en permettant 
la personnalisation de certains paramètres comme le destinataire.

L'objectif principal est de permettre une exécution facile depuis la console Docker de Geocontrib 
pour envoyer des e-mails de test.

Utilisation :
-----------
1. Assurez-vous que vous êtes dans l'environnement Docker de Geocontrib.
2. Exécutez le script comme suit :
   python send-mail.py --to [adresse_email_destinataire] --subject "[sujet_du_mail]"

Exemple :
--------
python send-mail.py --to pgros@neogeo.fr --subject "ceci est un test"

Note :
-----
Le script utilisera la configuration e-mail par défaut de Geocontrib pour l'expéditeur et 
d'autres paramètres. Vous n'avez besoin de fournir que le destinataire et le sujet.

Auteur : Timothée Poussard
Date : 27/10/2023
"""

# Configuration du logging
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Initialisation de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
try:
    django.setup()
    logger.debug("Django initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing Django: {e}")
    exit(1)

def main():
    logger.debug("Starting main function...")
    parser = argparse.ArgumentParser(description='Send an email using Django.')
    parser.add_argument('--to', required=True, help='Recipient email address.')
    parser.add_argument('--subject', required=True, help='Email subject.')
    parser.add_argument('--message', default='', help='Email message.')

    args = parser.parse_args()
    logger.debug(f"Arguments parsed: to={args.to}, subject={args.subject}, message={args.message}")

    logger.debug("Preparing to send email...")
    try:
        send_mail(
            args.subject,
            args.message,
            None,  # En laissant l'expéditeur à None, Django utilisera DEFAULT_FROM_EMAIL
            [args.to],
            fail_silently=False,
        )
        logger.info(f"Email sent successfully to {args.to} with subject '{args.subject}'.")
    except Exception as e:
        # Vérifier si l'erreur est "Relay access denied"
        if 'Relay access denied' in str(e):
            logger.error("Failed to send email due to SMTP relay access denied. Check your SMTP server configuration.")
        else:
            logger.error(f"Error sending email: {e}")

    logger.debug("Exiting main function...")

if __name__ == "__main__":
    main()
