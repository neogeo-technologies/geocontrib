from api.utils.db_utils import fetch_raw_data


def get_values_pre_enregistrés(name, pattern):
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
            )
            SELECT values from NewScores where values like '{pattern}%%'
            LIMIT 10;
            """.format(
              name=name,
              pattern=pattern)
    return fetch_raw_data('default', sql)


