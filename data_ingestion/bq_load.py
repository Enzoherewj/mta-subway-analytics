import os
from datetime import datetime
from google.cloud import bigquery
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# Constants
PROJECT_ID = os.getenv('GCP_PROJECT_ID')
BUCKET_NAME = os.getenv('GCP_BUCKET_NAME')
DATASET_ID = os.getenv('GCP_DATASET_ID')

def create_table_schema():
    """Define the BigQuery table schema with proper types."""
    return [
        bigquery.SchemaField("transit_timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("transit_mode", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("station_complex_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("station_complex", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("borough", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("payment_method", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("fare_class_category", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("ridership", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("transfers", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("latitude", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("longitude", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("georeference", "GEOGRAPHY", mode="REQUIRED"),
    ]

def create_or_update_table(client, year, force_recreate=False):
    """Create or update the BigQuery table for a specific year."""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.mta_ridership_{year}"
    
    # Define table schema
    schema = create_table_schema()
    
    # Configure partitioning and clustering
    table = bigquery.Table(table_id, schema=schema)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="transit_timestamp"
    )
    table.clustering_fields = ["station_complex_id", "payment_method"]
    
    try:
        if force_recreate:
            # Delete the table if it exists
            client.delete_table(table_id, not_found_ok=True)
            print(f"Deleted existing table {table_id}")
        
        # Create or update the table
        table = client.create_table(table, exists_ok=True)
        print(f"Created or updated table {table_id}")
    except Exception as e:
        print(f"Error creating/updating table: {e}")
        if "Cannot add fields" in str(e):
            print("\nThe table exists with a different schema. Use --force-recreate to drop and recreate the table.")
            raise
    return table

def load_data_from_gcs(client, year, month):
    """Load data from GCS to BigQuery for a specific year and month."""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.mta_ridership_{year}"
    uri = f"gs://{BUCKET_NAME}/mta_ridership/{year}/mta_ridership_{year}_{month:02d}.csv"
    
    # Check if data for this month already exists
    query = f"""
    SELECT COUNT(*) as count
    FROM `{table_id}`
    WHERE DATE(transit_timestamp) >= DATE '{year}-{month:02d}-01'
      AND DATE(transit_timestamp) < DATE_ADD(DATE '{year}-{month:02d}-01', INTERVAL 1 MONTH)
    """
    query_job = client.query(query)
    result = next(query_job.result())

    if result.count > 0:
        print(f"Data for {year}-{month:02d} already exists in the table. Skipping...")
        return
    
    job_config = bigquery.LoadJobConfig(
        schema=create_table_schema(),
        skip_leading_rows=1,  # Skip header row
        source_format=bigquery.SourceFormat.CSV,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,  # Append new data to existing table
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="transit_timestamp"
        ),
        clustering_fields=["station_complex_id", "payment_method"]
    )
    
    load_job = client.load_table_from_uri(
        uri,
        table_id,
        job_config=job_config
    )
    
    load_job.result()  # Wait for the job to complete
    
    destination_table = client.get_table(table_id)
    print(f"Loaded {destination_table.num_rows} rows into {table_id}")

def main():
    parser = argparse.ArgumentParser(description='Load MTA data from GCS to BigQuery')
    parser.add_argument('--year', type=int, help='Year to process')
    parser.add_argument('--month', type=int, help='Month to process')
    parser.add_argument('--all-years', action='store_true', help='Process all years (2023-2025)')
    parser.add_argument('--force-recreate', action='store_true', help='Drop and recreate tables if they exist')
    args = parser.parse_args()
    
    # Initialize BigQuery client
    client = bigquery.Client()
    
    if args.all_years:
        # Process all years
        for year in range(2023, 2026):  # 2023, 2024, 2025
            print(f"\nProcessing year {year}...")
            create_or_update_table(client, year, args.force_recreate)
            
            # Determine end month based on year
            end_month = 12 if year < 2025 else 4  # 2025 only goes up to April
            
            for month in range(1, end_month + 1):
                print(f"Loading data for {year}-{month:02d}...")
                load_data_from_gcs(client, year, month)
    elif args.year:
        # Process specific year
        create_or_update_table(client, args.year, args.force_recreate)
        
        if args.month:
            # Process specific month
            print(f"Loading data for {args.year}-{args.month:02d}...")
            load_data_from_gcs(client, args.year, args.month)
        else:
            # Process all months for the year
            end_month = 12 if args.year < 2025 else 4  # 2025 only goes up to April
            for month in range(1, end_month + 1):
                print(f"Loading data for {args.year}-{month:02d}...")
                load_data_from_gcs(client, args.year, month)
    else:
        parser.error("Either --year or --all-years must be specified")

if __name__ == "__main__":
    main() 