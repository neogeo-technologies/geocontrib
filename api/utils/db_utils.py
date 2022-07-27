from django.db import connections
from sqlalchemy import text


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


def fetch_raw_data(database, sql, **params):
    """
    Permet de se connecter à 'database' à partir de la 'Route' définie
    dans la variable settings.DATABASE et d'y exécuter une requete 'sql'.
    Ferme la connection en fin de traîtement.
    """
    with connections[database].cursor() as cursor:
        cursor.execute(sql, params)
        list_dict = list_fetch_all(cursor)
        
        if not list_dict or not len(list_dict):
            return []
    return list_dict