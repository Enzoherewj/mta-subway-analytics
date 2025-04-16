{{
    config(
        materialized='table',
        schema='marts'
    )
}}

with hourly_aggregates as (
    select
        date_hour,
        date_day,
        hour_of_day,
        day_of_week,
        cleaned_borough as borough,
        sum(ridership) as total_ridership,
        count(distinct station_complex_id) as active_stations
    from {{ ref('stg_mta_ridership') }}
    group by 1, 2, 3, 4, 5
),

daily_aggregates as (
    select
        date_day,
        day_of_week,
        borough,
        sum(total_ridership) as daily_ridership,
        avg(total_ridership) as avg_hourly_ridership,
        max(total_ridership) as peak_hourly_ridership,
        min(total_ridership) as min_hourly_ridership,
        count(distinct hour_of_day) as hours_with_data
    from hourly_aggregates
    group by 1, 2, 3
),

weekly_patterns as (
    select
        day_of_week,
        borough,
        avg(daily_ridership) as avg_daily_ridership,
        avg(peak_hourly_ridership) as avg_peak_hourly_ridership,
        avg(min_hourly_ridership) as avg_min_hourly_ridership
    from daily_aggregates
    group by 1, 2
)

select
    d.*,
    w.avg_daily_ridership as typical_daily_ridership,
    w.avg_peak_hourly_ridership as typical_peak_hourly_ridership,
    w.avg_min_hourly_ridership as typical_min_hourly_ridership,
    -- Calculate ridership as percentage of typical
    case
        when w.avg_daily_ridership = 0 then 100
        else (d.daily_ridership / w.avg_daily_ridership * 100)::int
    end as ridership_vs_typical_pct
from daily_aggregates d
left join weekly_patterns w
    on d.day_of_week = w.day_of_week
    and d.borough = w.borough 