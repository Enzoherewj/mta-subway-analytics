{{
    config(
        materialized='table',
        schema='staging'
    )
}}

with source_data as (
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
        -- Extract useful time components
        date_trunc('day', transit_timestamp) as date_day,
        date_trunc('hour', transit_timestamp) as date_hour,
        extract(hour from transit_timestamp) as hour_of_day,
        extract(dow from transit_timestamp) as day_of_week
    from {{ source('mta', 'raw_ridership') }}
    {% if var('is_test_run', true) %}
    limit {{ var('row_limit', 100) }}
    {% endif %}
),

cleaned as (
    select
        *
    from source_data
)

select * from cleaned 