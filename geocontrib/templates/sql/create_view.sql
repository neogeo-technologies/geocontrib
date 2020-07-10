{% load app_filters %}

DROP VIEW IF EXISTS  {{ schema }}.{{ view_name }};
CREATE OR REPLACE VIEW {{ schema }}.{{ view_name }} AS
  SELECT {% for data in fds_data %}
      geocontrib_feature.{{ data|lookup:'related_field' }}{% if data|lookup:'alias'|length > 0 %} AS {{ data|lookup:'alias' }}{% endif %},
  {% endfor %}
    {% for data in cfs_data %}{% if data|lookup:'field_type' in 'integer,decimal,date,boolean' %}
    (geocontrib_feature.feature_data ->> '{{ data|lookup:'name' }}'::text)::{{ data|lookup:'field_type' }}
    {% else %}geocontrib_feature.feature_data ->> '{{ data|lookup:'name' }}'::text{% endif %}
    AS {% if data|lookup:'alias'|length > 0 %}{{ data|lookup:'alias'|slugify }}{% else %}{{ data|lookup:'name' }}{% endif %}{% if not forloop.last %},{% endif%}
    {% endfor %}
  FROM geocontrib_feature
  WHERE
      geocontrib_feature.feature_type_id = '{{ feature_type_id }}'
      AND geocontrib_feature.status IN ({% for stat in status %}'{{stat}}'{% if not forloop.last %}, {% endif%}{% endfor %});
ALTER TABLE {{ schema }}.{{ view_name }} OWNER TO {{ user }};
