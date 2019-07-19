"""
Si modifications sur ce fichier, générer migrations pour que les listes de choix
soient à jours entre application et base.
"""

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
    (MODERATOR, 'Moderateur'),
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
