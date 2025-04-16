{{
    config(
        materialized='table',
        schema='staging'
    )
}}

with source_data as (
    {{ get_ridership_data() }}
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