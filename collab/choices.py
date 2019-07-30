"""
Si modifications sur ce fichier, générer migrations pour que les listes de choix
soient à jours entre application et base.
"""

######################
# CUSTOM FIELD TYPES #
######################

TYPE_CHOICES = (
    ("boolean", "Booléen"),
    ("char", "Chaîne de caractères"),
    ("date", "Date"),
    ("integer", "Entier"),
    ("decimal", "Décimale"),
    ("text", "Champ texte"),
)

######################
# LEVELS PERMISSIONS #
######################

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
    (MODERATOR, 'Modérateur'),
    (ADMIN, 'Admin'),
)

ALL_LEVELS = LOWER_LEVELS + EXTENDED_LEVELS


##################
# EVENTS CHOICES #
##################

COMMENT = 'comment'
FEATURE = 'feature'
ATTACHMENT = 'attachment'
PROJECT = 'project'

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
    ('update', "Modification"),
    ('delete', "Suppression"),
)


STATE_CHOICES = (
    ('pending', "Tâche en attente d'exécution"),
    ('failed', "Echec de la tâche"),
    ('succesful', "Tâche terminée avec succés"),
)

FREQUENCY_CHOICES = (
    ('never', 'Jamais'),
    ('instantly', 'Instantanément'),
    ('daily', 'Quotidienne'),
    ('weekly', 'Hebdomadaire'),
)
