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
    ("list", "Liste de valeurs"),
    ("pre_recorded_list", "Liste de valeurs pré-enregistrées"),
    ("multi_choices_list", "Liste à choix multiples"),
    ("integer", "Nombre entier"),
    ("decimal", "Nombre décimal"),
    ("text", "Texte multiligne"),
)

######################
# LEVELS PERMISSIONS #
######################

ANONYMOUS = 'anonymous'
LOGGED_USER = 'logged_user'
CONTRIBUTOR = 'contributor'
SUPER_CONTRIBUTOR = 'super_contributor'
MODERATOR = 'moderator'
ADMIN = 'admin'

LOWER_LEVELS = (
    (ANONYMOUS, 'Utilisateur anonyme'),
    (LOGGED_USER, 'Utilisateur connecté'),
    (CONTRIBUTOR, 'Contributeur'),
)

EXTENDED_LEVELS = (
    (SUPER_CONTRIBUTOR, 'Super Contributeur'),
    (MODERATOR, 'Modérateur'),
    (ADMIN, 'Administrateur projet'),
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
    ('archive', "Archivage"),
    ('delete', "Suppression"),
)


STATE_CHOICES = (
    ('pending', "Tâche en attente d'exécution"),
    ('failed', "Echec de la tâche"),
    ('successful', "Tâche terminée avec succès"),
)

FREQUENCY_CHOICES = (
    ('never', 'Jamais'),
    ('instantly', 'Instantanément'),
    ('daily', 'Quotidienne'),
    ('weekly', 'Hebdomadaire'),
)
