/*skip-formatter*/
SELECT *
FROM   examples_entity
WHERE  id = {{ id }}
   {% if name %}
   and name ilike {{ name }}
   {% endif %}
