from django.core.management import call_command
from django.db import connection
from django.db import models
from django.http import JsonResponse
from django.shortcuts import render
import io
import shutil
from ..actions import create_model

APP_NAME = __package__.split('.')[0]


def ajout_signalement(request):

    if request.method == 'POST':
        if request.POST.getlist('type') and request.POST.get('sig_type') and request.POST.getlist('type'):
            generate_model(request.POST.get('sig_type'), request.POST.getlist('nom'), request.POST.getlist('type'))
            return JsonResponse("ok", status=200, safe=False)
        else:
            return JsonResponse("nok", status=200, safe=False)
    else:
        return render(request, APP_NAME + '/ajout_signalement.html')


def generate_model(sig_type, nom, type):

    fields = {}
    application = APP_NAME
    module = 'config.' + application
    CHAR = []
    FLOAT = []
    INT = []
    DATE = []

    for elt in range(0, len(type)):
        if nom[elt] and type[elt]:
            CHAR.append(models.CharField(max_length=255))
            DATE.append(models.DateTimeField(blank=True, null=True))
            FLOAT.append(models.FloatField())
            INT.append(models.IntegerField())
            MODEL_DJANGO = {
                'string': CHAR[elt],
                'int': INT[elt],
                'date': DATE[elt],
                'float': FLOAT[elt]
            }
            fields[nom[elt]] = MODEL_DJANGO[type[elt]]

    # ajout du nom de la table
    table_name = application + "_" + 'type' + '_' + sig_type
    # creation modele
    model = create_model('type'+'_'+sig_type, fields,
                         app_label=application,
                         module=module,
                         admin_opts={})
    try:
        with connection.schema_editor() as editor:
            editor.create_model(model)
    except Exception as e:
        pass
    # generation du fichier models.py
    out = io.StringIO()
    call_command('inspectdb', table_name, stdout=out)

    with open(application + """/models/models_type_{signalement}.py""".format(
              signalement=sig_type), 'a') as fd:
        out.seek(0)
        shutil.copyfileobj(out, fd)
