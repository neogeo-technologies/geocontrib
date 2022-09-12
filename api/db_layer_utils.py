from api.utils.db_utils import fetch_raw_data


def get_values_pre_enregistrés(name, pattern=''):
    """
        Fonction recuperant les valeurs pré
        enregistrées.
    """
    sql = """
            WITH NewScores AS (
                SELECT TRIM('"' 
                    from json_array_elements(
                        geocontrib_prerecordedvalues.values::json)::text)
                    as values
                FROM   geocontrib_prerecordedvalues
                WHERE  name = '{name}'
            ) SELECT values from NewScores
            """.format(
                name=name,
            )
    if pattern:
        sql+="""
             WHERE values like '{pattern}%%'
        """.format(
            pattern=pattern)

    sql += " LIMIT 10;"
    return fetch_raw_data('default', sql)


