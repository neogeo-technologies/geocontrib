import json
from django.core.serializers.json import DjangoJSONEncoder


# TODO@cbenhabib: tester une solution avec l'utilisation de DRF pour
# les sérializations et déserialization d'une instance Feature
def save_custom_fields(extras, input_data):
    # On ne sauvegarde en base que les champs definis dans les custom_fields
    if isinstance(input_data, dict) and extras.exists():
        stringfied = json.dumps(input_data, cls=DjangoJSONEncoder)
        jsonified = json.loads(stringfied)
        newdict = {field_name: jsonified.get(field_name) for field_name in extras.values_list('name', flat=True)}
        return newdict
    return {}
