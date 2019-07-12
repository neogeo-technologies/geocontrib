"""
Propositions d'usage de listes de choix
Redondant mais permet de faire des controles de type:
>>>if user1.level == choices.CONTRIBUTOR: [...]
Ces constantes sont referencées dans __init_.py pour les importer toutes
On pourrai utiliser des libellée au lieu de symboles, car c'est la valeur stocké
en base, on pourra ainsi lire les tables plus facilement
"""

ANONYMOUS = 'anonymous'
LOGGED_USER = 'logged_user'
CONTRIBUTOR = 'contributor'
MODERATOR = 'moderator'
ADMIN = 'admin'

LOWER_LEVELS = (
    (ANONYMOUS, 'Utilisateur anonyme'),
    (LOGGED_USER, 'Utilisateur connecté'),
    (CONTRIBUTOR, 'Contributeur'),
)

EXTENDED_LEVELS = (
    (MODERATOR, 'Moderateur'),
    (ADMIN, 'Admin'),
)

ALL_LEVELS = LOWER_LEVELS + EXTENDED_LEVELS


COMMENT = 'comment'
FEATURE = 'feature'
ATTACHMENT = 'feature'
PROJECT = 'Projet'

RELATED_MODELS = (
    (COMMENT, 'Commentaire'),
    (FEATURE, 'Signalement'),
)

OTHERS_MODELS = (
    (ATTACHMENT, 'Pièce jointe'),
    (PROJECT, 'Projet'),
)

EXTENDED_RELATED_MODELS = RELATED_MODELS + OTHERS_MODELS

EVENT_TYPES = (
    ('create', "Création"),
    ('update_attachment', "Modification d'une pièce jointe"),
    ('update_loc', 'Modification de la localisation'),
    ('update_attrs', "Modification d’un attribut"),
    ('update_status', "Changement de statut"),
    ('delete', 'Suppression'),
)


STATE_CHOICES = (
    ('pending', "Tâche en attente d'exécution"),
    ('failed', "Echec de la tâche"),
    ('succesful', "Tâche terminée avec succés"),
)

FREQUENCY_CHOICES = (
    ('instantly', 'Instantanément'),
    ('daily', 'Quotidienne'),
    ('weekly', 'Hebdomadaire'),
)
