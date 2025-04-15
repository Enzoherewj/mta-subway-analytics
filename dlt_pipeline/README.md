# MTA Subway Data Ingestion Pipeline

This directory contains the data ingestion pipeline for MTA Subway ridership data using `dlt`.

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
     - `GCP_DATASET_ID`: Target BigQuery dataset name

## Usage

Run the ingestion pipeline:
```bash
python mta_ingest.py
```

## Data Range

The pipeline ingests data from:
- Start: 2023-01-01
- End: 2025-04-01

## Pipeline Details

- Uses `dlt` for data loading
- Implements pagination to handle large datasets
- Loads data into BigQuery
- Includes error handling and logging 