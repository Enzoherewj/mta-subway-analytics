# dbt Models for MTA Subway Analytics

This directory contains dbt models for transforming MTA subway ridership data into analytics-ready tables.

## Model Structure

### Staging Layer (`models/staging/`)
- `stg_mta_ridership.sql`
  - Source: Raw MTA ridership data from BigQuery
  - Purpose: Initial data cleaning and type casting
  - Key transformations:
    - Casting ridership to FLOAT
    - Standardizing timestamp formats
    - Basic data validation

### Mart Layer (`models/marts/`)
- `mart_station_ridership.sql`
  - Purpose: Station-level analytics
  - Key metrics:
    - Average daily ridership
    - Peak and minimum ridership
    - Ridership intensity score (0-100)
    - Days with data
  - Used for: Station performance analysis, capacity planning

- `mart_temporal_trends.sql`
  - Purpose: Time-based ridership patterns
  - Key metrics:
    - Daily ridership trends
    - Hourly patterns
    - Weekly patterns
    - Ridership vs typical percentage
  - Used for: Temporal analysis, anomaly detection

## Model Dependencies
```
stg_mta_ridership
    ├── mart_station_ridership
    └── mart_temporal_trends
```

## Usage

### Development
```bash
# Run with test data (100 rows)
dbt build

# Run with full data
dbt build --vars 'is_test_run: false'
```

### Production
```bash
# Run all models
dbt build --vars 'is_test_run: false'

# Run specific model
dbt build --select mart_station_ridership
```

## Configuration
- Test data limit: 100 rows (configurable in dbt_project.yml)
- Schema: mta_subway_analytics
- Target: BigQuery