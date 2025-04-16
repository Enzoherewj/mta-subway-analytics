{{
    config(
        materialized='table',
        schema='staging'
    )
}}

with source_data as (
    select
        transit_timestamp,
        station_complex_id,
        station_complex,
        borough,
        payment_method,
        ridership,
        transfers,
        latitude,
        longitude,
        -- Extract useful time components
        date_trunc('day', transit_timestamp) as date_day,
        date_trunc('hour', transit_timestamp) as date_hour,
        extract(hour from transit_timestamp) as hour_of_day,
        extract(dow from transit_timestamp) as day_of_week
    from {{ source('mta', 'raw_ridership') }}
),

cleaned as (
    select
        *,
        -- Clean station names
        trim(station_complex) as cleaned_station_name,
        -- Clean borough names
        case 
            when borough = 'BROOKLYN' then 'Brooklyn'
            when borough = 'MANHATTAN' then 'Manhattan'
            when borough = 'QUEENS' then 'Queens'
            when borough = 'BRONX' then 'Bronx'
            when borough = 'STATEN ISLAND' then 'Staten Island'
            else borough
        end as cleaned_borough
    from source_data
)

select * from cleaned 