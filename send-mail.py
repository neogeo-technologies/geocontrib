import os
import django
import argparse
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

# Initialisation de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def main():
    parser = argparse.ArgumentParser(description='Send an email using Django.')
    parser.add_argument('--to', required=True, help='Recipient email address.')
    parser.add_argument('--subject', required=True, help='Email subject.')
    parser.add_argument('--message', default='', help='Email message.')

    args = parser.parse_args()

    # Utilisez la fonction send_mail de Django pour envoyer l'e-mail
    send_mail(
        args.subject,
        args.message,
        None,  # En laissant l'expéditeur à None, Django utilisera DEFAULT_FROM_EMAIL comme expéditeur par défaut
        [args.to],
        fail_silently=False,
    )

if __name__ == "__main__":
    main()
