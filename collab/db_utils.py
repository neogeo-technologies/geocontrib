import datetime
from datetime import timedelta
import dateutil.parser
from django.db import connections
from django.utils import timezone
import re


def commit_data(database, sql):

    """
    Cette fonction permet de se connecter à 'database' à partir de la 'Route'
    définie dans la variable settings.DATABASE et d'y exécuter une requete 'sql'
    d'insertion.
    Ferme la connection en fin de traîtement.
    """
    status = True
    try:
        connections[database].cursor().execute(sql)
        connections[database].commit()
    except Exception as e:
        status = str(e)
    finally:
        connections[database].cursor().close()
        return status


def list_fetch_all(cursor):
    """
    Retourne sous forme d'une liste de dictionnaires les valeurs d'une requete:
    FORMAT = [{
        'field_name1': field_value1,
        'field_name2': field_value2
        },{
        'field_name1': field_value1,
        'field_name2': field_value2
        }...]
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def fetch_raw_data(database, sql):
    """
    Permet de se connecter à 'database' à partir de la 'Route' définie
    dans la variable settings.DATABASE et d'y exécuter une requete 'sql'.
    Ferme la connection en fin de traîtement.
    """
    with connections[database].cursor() as cursor:
        cursor.execute(sql)
        list_dict = list_fetch_all(cursor)
        if not list_dict or not len(list_dict):
            return []
    return list_dict


def fetch_first_row(database, sql):
    """
    idem que fetch_raw_data mais retourne uniquement la premiere ligne
    sous forme d'un dictionnaire.

    """
    with connections[database].cursor() as cursor:
        cursor.execute(sql)
        list_dict = list_fetch_all(cursor)
        if not list_dict or not len(list_dict):
            return {}
    return list_dict[0]


def edit_feature_sql(data):
    """
        Get sql for the modification of a feature
     """
    # remove the csrfmiddlewaretoken key
    data.pop('csrfmiddlewaretoken', None)
    data.pop('feature', None)
    add_sql = ""
    date_pattern = re.compile('^[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4}$')
    # replace 'on' by 'true'
    for key, val in data.items():
        if date_pattern.match(str(val)):
            if val:
                format_date = timezone.make_aware(dateutil.parser.parse(val), timezone.get_current_timezone())
                add_sql += """,{key}='{format_date}'""".format(
                           key=str(key),
                           format_date=str(format_date))
            else:
                add_sql += """,{key}=NULL""".format(
                           key=str(key))
        elif val == "on":
            add_sql += """,{key}={val}""".format(
                    key=str(key),
                    val=True)
        else:
            add_sql += """,{key}='{val}'""".format(
                    key=str(key),
                    val=str(val))

    return add_sql


def create_feature_sql(data):
    """
        Get sql for the creation of a feature
     """
    # remove the csrfmiddlewaretoken key
    data.pop('csrfmiddlewaretoken', None)
    data.pop('feature', None)
    # replace 'on' by 'true'
    for key, val in data.items():
        if val == "on":
            data[key] = 'True'
    # remove empty keys -> A AMELIORER "'" !!!!!!!!!
    data = {k: v for k, v in data.items() if v}
    data_keys = " "
    data_values = " "
    if data.keys():
        data_keys = ' , ' + ' , '.join(list(data.keys()))
    if data.values():
        data_values = " , '" + "' , '".join(list(data.values())) + "'"

    return data_keys, data_values
