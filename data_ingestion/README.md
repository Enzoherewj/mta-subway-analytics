# MTA Subway Data Ingestion Pipeline

This directory contains the data ingestion pipeline for MTA Subway ridership data. The pipeline fetches data from the MTA API and stores it in Google Cloud Storage (GCS).

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the following variables in `.env`:
     - `MTA_API_TOKEN`: Your MTA API token
     - `GOOGLE_APPLICATION_CREDENTIALS`: Path to your GCP service account key
     - `GCP_PROJECT_ID`: Your GCP project ID
     - `GCP_BUCKET_NAME`: Target GCS bucket name

## Usage

Run the ingestion pipeline:
```bash
# Test run with limited records
python mta_ingest.py --test --test-limit 200

# Full run
python mta_ingest.py
```

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