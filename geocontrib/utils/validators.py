import logging
import magic

from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


@deconstructible
class MimetypeValidator(object):
    """
    @from https://github.com/devangpadhiyar/django-validators
    """
    def __init__(self, mimetypes, message=None, code='file-type'):
        self.mimetypes = mimetypes
        self.message = message
        self.code = code

    def __call__(self, value):
        try:
            mime = magic.from_buffer(value.read(1024), mime=True)
            value.seek(0)
            if mime not in self.mimetypes:
                if not self.message:
                    raise ValidationError(
                        "Ce type de fichier '{}' n'est pas pris en charge".format(mime),
                        code=self.code
                    )
                else:
                    raise ValidationError(self.message, code=self.code)
        except AttributeError:
            logger.exception('Error eval mime from magic-python')
            raise ValidationError(
                "Erreur à la validation du type de fichier", code=self.code)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.mimetypes == other.mimetypes and
            self.message == other.message and
            self.code == other.code
        )


validate_json = MimetypeValidator(mimetypes=('application/json', 'text/plain'))
