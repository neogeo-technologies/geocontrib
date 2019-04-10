from django.contrib import admin
from django.apps import apps

app = apps.get_app_config('collab')

for model_name, model in app.models.items():

    if 'auth' not in model_name and 'django' not in model_name:
        admin.site.register(model)
