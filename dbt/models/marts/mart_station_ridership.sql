{{
    config(
        materialized='table',
        schema='marts'
    )
}}

with daily_station_stats as (
    select
        date_day,
        station_complex_id,
        cleaned_station_name as station_name,
        cleaned_borough as borough,
        latitude,
        longitude,
        sum(ridership) as total_ridership,
        count(distinct date_hour) as hours_with_data,
        avg(ridership) as avg_hourly_ridership
    from {{ ref('stg_mta_ridership') }}
    group by 1, 2, 3, 4, 5, 6
),

station_metrics as (
    select
        station_complex_id,
        station_name,
        borough,
        latitude,
        longitude,
        avg(total_ridership) as avg_daily_ridership,
        max(total_ridership) as max_daily_ridership,
        min(total_ridership) as min_daily_ridership,
        count(distinct date_day) as days_with_data
    from daily_station_stats
    group by 1, 2, 3, 4, 5
)

select
    *,
    -- Calculate ridership intensity score (0-100)
    case
        when max_daily_ridership = min_daily_ridership then 50
        else ((avg_daily_ridership - min_daily_ridership) / 
              (max_daily_ridership - min_daily_ridership) * 100)::int
    end as ridership_intensity_score
from station_metrics 