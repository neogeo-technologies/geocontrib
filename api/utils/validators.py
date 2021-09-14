import magic
from rest_framework.serializers import ValidationError

IMAGE_MIME_TYPES = (
    'image/bmp',
    'image/jpg',
    'image/jpeg',
    'image/tiff',
    'image/png',
)


def validate_image_file(value):
    try:
        mime = magic.from_buffer(value.read(1024), mime=True)
        value.seek(0)
        if mime not in IMAGE_MIME_TYPES:
            raise ValidationError(
                "Ce type de fichier '{}' n'est pas pris en charge".format(mime),
                code='file-type'
            )
    except AttributeError:
        raise ValidationError("Erreur à la validation du type de fichier", code='file-type')
