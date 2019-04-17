from django.db import connections


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
        status = False
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
