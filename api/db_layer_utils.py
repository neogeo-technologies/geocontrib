from django.db import connection

def get_pre_recorded_values(name, pattern=''):
    """
    Retrieves pre-recorded values from the database based on a given pattern.

    :param name: The name of the pre-recorded values to retrieve.
    :param pattern: An optional search pattern. If provided, only values containing this pattern will be returned.
    :param limit: An optional limit to the number of values to retrieve.
    :return: A list of values that match the given name and optional pattern.
    """

    with connection.cursor() as cursor:
        sql = """
            WITH NewScores AS (
                SELECT TRIM(BOTH '"' FROM json_array_elements(geocontrib_prerecordedvalues.values::json)::text) AS values
                FROM geocontrib_prerecordedvalues
                WHERE name = %s
            )
            SELECT values FROM NewScores
        """

        params = [name]  # Parameters for the SQL query

        if pattern:
            sql += " WHERE lower(values) LIKE lower(%s)"
            params.append(f'%{pattern}%')  # Appending the pattern surrounded by % for partial matching

        sql += " ORDER BY values"

        print("Executing SQL:", sql)
        print("With parameters:", params)

        cursor.execute(sql, params)
        rows = cursor.fetchall()

    return [row[0] for row in rows]