from django.db import connection

def get_pre_recorded_values(name, pattern='', limit=50, offset=0, with_count=False):
    """
    Retrieves pre-recorded values from the database based on a given pattern.
    - Insensitive to case, accents (via unaccent), and hyphens.
    - Prioritizes prefix matches, then substring position, then length, then alphabetical order.
    Supports pagination via limit/offset and can return total count.
    """

    with connection.cursor() as cursor:
        base_cte = """
            WITH vals AS (
              SELECT TRIM(BOTH '"' FROM json_array_elements(geocontrib_prerecordedvalues.values::json)::text) AS value
              FROM geocontrib_prerecordedvalues
              WHERE name = %s
            )
        """
        params = [name]

        if pattern:
            sql = base_cte + """
                SELECT value,
                       COUNT(*) OVER() AS total,
                       CASE
                         WHEN unaccent(regexp_replace(lower(value), '[-]', ' ', 'g'))
                              LIKE unaccent(regexp_replace(lower(%s), '[-]', ' ', 'g')) || '%%' THEN 0
                         WHEN unaccent(regexp_replace(lower(value), '[-]', ' ', 'g'))
                              LIKE '%%' || unaccent(regexp_replace(lower(%s), '[-]', ' ', 'g')) || '%%' THEN 1
                         ELSE 2
                       END AS rank_prefix,
                       STRPOS(unaccent(regexp_replace(lower(value), '[-]', ' ', 'g')),
                              unaccent(regexp_replace(lower(%s), '[-]', ' ', 'g'))) AS rank_pos
                FROM vals
                WHERE unaccent(regexp_replace(lower(value), '[-]', ' ', 'g'))
                      LIKE '%%' || unaccent(regexp_replace(lower(%s), '[-]', ' ', 'g')) || '%%'
                ORDER BY rank_prefix ASC, rank_pos ASC, LENGTH(value) ASC, value ASC
                LIMIT %s OFFSET %s;
            """
            params += [pattern, pattern, pattern, pattern, int(limit), int(offset)]
        else:
            sql = base_cte + """
                SELECT value,
                       COUNT(*) OVER() AS total,
                       0 AS rank_prefix,
                       0 AS rank_pos
                FROM vals
                ORDER BY value ASC
                LIMIT %s OFFSET %s;
            """
            params += [int(limit), int(offset)]

        cursor.execute(sql, params)
        rows = cursor.fetchall()

    values = [r[0] for r in rows]
    total = rows[0][1] if rows else 0
    return (values, total) if with_count else values
