# Data Ingestion Pipeline

This directory contains scripts for ingesting MTA subway ridership data and loading it into BigQuery.

## Files

### mta_ingest.py
- Ingests data from MTA API
- Processes data in monthly batches
- Stores raw CSV files in Google Cloud Storage
- Supports test mode with limited data

### bq_load.py
- Loads data from GCS into BigQuery
- Creates/updates tables with proper schema
- Handles partitioning and clustering
- Supports both full and partial data loading

### Environment Files
- `.env`: Contains actual environment variables (not tracked in git)
- `.env.example`: Template for required environment variables

## Environment Variables

Create a `.env` file with the following variables:
```
# MTA API Configuration
MTA_API_TOKEN=your_api_token
MTA_API_BASE_URL=https://data.ny.gov/resource/wujg-7c2s.json

# GCP Configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/gcp_credentials.json
GCP_PROJECT_ID=your_project_id
GCP_DATASET_ID=your_dataset_id
GCP_BUCKET_NAME=your_bucket_name
```

## Usage

### Data Ingestion
```bash
# Full ingestion
python mta_ingest.py

# Test ingestion (limited data)
python mta_ingest.py --test --test-limit 100
```

### BigQuery Loading
```bash
# Load all years
python bq_load.py --all-years

# Load specific year/month
python bq_load.py --year 2023 --month 1

# Force recreate tables
python bq_load.py --all-years --force-recreate
```

## Dependencies
- python-dotenv
- requests
- tqdm
- google-cloud-storage
- google-cloud-bigquery

## Data Range

The pipeline ingests data from:
- Start: 2023-01-01
- End: 2025-04-01

## Pipeline Details

- Fetches data from two MTA APIs:
  - 2020-2024 data: `https://data.ny.gov/resource/wujg-7c2s.json`
  - 2025 data: `https://data.ny.gov/resource/5wq4-mkjj.json`
- Processes data in batches of 50,000 records
- Stores data in GCS with the following structure:
  ```
  gs://bucket/mta_ridership/
  ├── 2023/
  │   ├── mta_ridership_2023_01.csv
  │   ├── mta_ridership_2023_02.csv
  │   └── ...
  ├── 2024/
  │   ├── mta_ridership_2024_01.csv
  │   ├── mta_ridership_2024_02.csv
  │   └── ...
  └── 2025/
      ├── mta_ridership_2025_01.csv
      ├── mta_ridership_2025_02.csv
      └── ...
  ```
- Includes progress bars for data fetching and processing
- Implements error handling and logging
- Supports test mode for quick validation 