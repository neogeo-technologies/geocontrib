from django.core.validators import RegexValidator


alphanumeric = RegexValidator(
    r'^[0-9a-zA-Z_-]*$',
    "Seuls les caractères alphanumeriques 0-9 a-z A-Z _ - sont autorisés. "
)
