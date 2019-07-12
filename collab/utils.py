import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime


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


def retreive_custom_fields(extras, output_data):
    res = {}
    if extras.exists():

        for row in extras.order_by('position').values('name', 'label', 'field_type'):

            if row['field_type'] == 'date':
                value = datetime.strptime(output_data.get(row['name']), "%Y-%m-%d")
            else:
                value = output_data.get(row['name'])
            res[row['name']] = {
                'label': row['label'],
                'field_type': row['field_type'],
                'value': value
            }
    return res
