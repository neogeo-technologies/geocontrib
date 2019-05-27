
GEOM_TYPE = (
    ('0', 'Point (POINT)'),
    ('1', 'Ligne (LINESTRING)'),
    ('2', 'Polygone (POLYGON)')
)

STATUS = (
    ('0', 'Brouillon'),
    ('1', 'En attente de publication'),
    ('2', 'Publié'),
    ('3', 'Archivé'),
)

STATUS_MODERE = (
    ('0', 'Brouillon'),
    ('1', 'En attente de publication'),
)


USER_TYPE = (
    ('0', 'Utilisateur anonyme'),
    ('1', 'Utilisateur connecté'),
    ('2', 'Contributeur'),
)

USER_TYPE_ARCHIVE = (
    ('0', 'Utilisateur anonyme'),
    ('1', 'Utilisateur connecté'),
    ('2', 'Contributeur'),
    ('3', 'Modérateur'),
    ('4', 'Administrateur'),
)
