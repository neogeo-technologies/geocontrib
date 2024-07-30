{% load app_filters %}

-- Drop the view if it exists to allow creation of the new or updated view.
DROP VIEW IF EXISTS {{ schema }}.{{ view_name }};

-- Create or replace the view with the specified name in the given schema.
CREATE OR REPLACE VIEW {{ schema }}.{{ view_name }} AS
  SELECT 
    {% for data in fds_data %}
        -- Select columns from the `geocontrib_feature` table based on feature details.
        -- The `lookup` filter dynamically determines the field to select and its alias.
        geocontrib_feature.{{ data|lookup:'related_field' }}
        {% if data|lookup:'alias'|length > 0 %}
            AS {{ data|lookup:'alias' }}  -- Rename the column if an alias is provided.
        {% endif %}
        {% if not forloop.last or cfs_data %}
            ,  -- Add a comma separator between columns, except for the last column.
        {% endif %}
    {% endfor %}

    {% for data in cfs_data %}
        -- Select columns from the `geocontrib_feature.feature_data` JSONB field based on custom fields.
        -- The field type determines how the value is cast and selected.
        {% if data|lookup:'field_type' in 'integer,decimal,date,boolean' %}
            -- Cast JSONB values to their respective data types if they are of a specific type.
            (geocontrib_feature.feature_data ->> '{{ data|lookup:'name' }}'::text)::{{ data|lookup:'field_type' }}
        {% else %}
            -- Select the value from the JSONB field as text if no specific casting is required.
            geocontrib_feature.feature_data ->> '{{ data|lookup:'name' }}'::text
        {% endif %}
        AS 
        {% if data|lookup:'alias'|length > 0 %}
            {{ data|lookup:'alias'|slugify }}  -- Use the provided alias if available, applying slugification.
        {% else %}
            {{ data|lookup:'name' }}  -- Use the field name as the column name if no alias is provided.
        {% endif %}
        {% if not forloop.last %}
            ,  -- Add a comma separator between columns, except for the last column.
        {% endif %}
    {% endfor %}
  FROM geocontrib_feature
  WHERE
      -- Filter records based on the feature type and status.
      geocontrib_feature.feature_type_id = '{{ feature_type_id }}'
      AND geocontrib_feature.status IN (
          {% for stat in status %}
              '{{ stat }}'  -- Include each status value provided in the list.
              {% if not forloop.last %}
                  ,  -- Add a comma separator between status values, except for the last value.
              {% endif %}
          {% endfor %}
      )
      AND geocontrib_feature.deletion_on IS NULL;  -- Exclude features where deletion_on is not null.

-- Set the ownership of the created view to the specified database user.
ALTER TABLE {{ schema }}.{{ view_name }} OWNER TO {{ user }};
