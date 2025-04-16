{% macro get_ridership_data() %}
    {% set years = ['2023', '2024', '2025'] %}
    {% set queries = [] %}
    
    {% for year in years %}
        {% set query %}
            select
                transit_timestamp,
                transit_mode,
                station_complex_id,
                station_complex,
                borough,
                payment_method,
                fare_class_category,
                ridership,
                transfers,
                latitude,
                longitude,
                georeference,
                DATE_TRUNC(transit_timestamp, DAY) as date_day,
                DATE_TRUNC(transit_timestamp, HOUR) as date_hour,
                EXTRACT(HOUR FROM transit_timestamp) as hour_of_day,
                EXTRACT(DAYOFWEEK FROM transit_timestamp) as day_of_week
            from {{ source('mta', 'mta_ridership_' ~ year) }}
        {% endset %}
        {% do queries.append(query) %}
    {% endfor %}
    
    {{ queries | join('\nunion all\n') }}
{% endmacro %} 