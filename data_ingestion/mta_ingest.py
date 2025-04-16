import os
import requests
import argparse
import csv
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict
from tqdm import tqdm
from google.cloud import storage

# Load environment variables
load_dotenv()

# Constants
MTA_2020_2024_URL = "https://data.ny.gov/resource/wujg-7c2s.json"
MTA_2025_URL = "https://data.ny.gov/resource/5wq4-mkjj.json"
API_TOKEN = os.getenv('MTA_API_TOKEN')
PAGE_SIZE = 50000  # Increased page size for API requests
START_DATE = "2023-01-01T00:00:00.000"
END_DATE = "2025-04-01T00:00:00.000"

# GCS settings
BUCKET_NAME = os.getenv('GCP_BUCKET_NAME')

def fetch_data_batch(url: str, year: int, month: int, offset: int, limit: int) -> List[Dict]:
    """
    Fetch a single batch of MTA subway ridership data for a specific month.
    """
    # Calculate start and end dates for the month
    start_date = f"{year}-{month:02d}-01T00:00:00.000"
    if month == 12:
        end_date = f"{year + 1}-01-01T00:00:00.000"
    else:
        end_date = f"{year}-{month + 1:02d}-01T00:00:00.000"
    
    params = {
        "$limit": limit,
        "$offset": offset,
        "$where": f"transit_timestamp >= '{start_date}' AND transit_timestamp < '{end_date}'",
        "$$app_token": API_TOKEN
    }
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return []

def write_to_csv(records: List[Dict], year: int, month: int) -> str:
    """
    Write records to a CSV file and return the file path.
    """
    filename = f"mta_ridership_{year}_{month:02d}.csv"
    local_path = f"/tmp/{filename}"
    
    # Write to CSV
    with open(local_path, 'w', newline='') as f:
        if records:
            writer = csv.DictWriter(f, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
    
    return local_path

def upload_to_gcs(local_path: str, year: int, month: int) -> str:
    """
    Upload file to GCS and return the GCS path.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    
    # Create GCS path - simplified to just year folder
    gcs_path = f"mta_ridership/{year}/{os.path.basename(local_path)}"
    blob = bucket.blob(gcs_path)
    
    # Upload file
    blob.upload_from_filename(local_path)
    
    # Clean up local file
    os.remove(local_path)
    
    return f"gs://{BUCKET_NAME}/{gcs_path}"

def process_month(url: str, year: int, month: int, test_mode: bool = False, test_limit: int = 100) -> int:
    """
    Process data for a specific month and save to GCS.
    """
    offset = 0
    total_records = 0
    records = []
    
    # Initialize progress bar
    pbar = tqdm(total=test_limit if test_mode else None, 
               desc=f"Processing {year}-{month:02d}",
               unit="records")
    
    while True:
        if test_mode and total_records >= test_limit:
            break
            
        batch = fetch_data_batch(url, year, month, offset, PAGE_SIZE)
        if not batch:
            break
            
        records.extend(batch)
        total_records += len(batch)
        pbar.update(len(batch))
        
        if test_mode and total_records >= test_limit:
            break
            
        if len(batch) < PAGE_SIZE:
            break
            
        offset += PAGE_SIZE
    
    # Process and upload the month's data
    if records:
        local_path = write_to_csv(records, year, month)
        gcs_path = upload_to_gcs(local_path, year, month)
        print(f"\nUploaded {len(records)} records to {gcs_path}")
    
    pbar.close()
    return total_records

def process_and_save_monthly(url: str, start_date: str, end_date: str, 
                           test_mode: bool = False, test_limit: int = 100):
    """
    Process data and save to GCS in monthly batches.
    """
    total_records = 0
    
    # Parse start and end dates
    start_dt = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%f')
    end_dt = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S.%f')
    
    # Process each month
    current_dt = start_dt
    while current_dt < end_dt:
        year = current_dt.year
        month = current_dt.month
        
        print(f"\nProcessing {year}-{month:02d}...")
        month_records = process_month(url, year, month, test_mode, test_limit)
        total_records += month_records
        
        # Move to next month
        if month == 12:
            current_dt = current_dt.replace(year=year + 1, month=1)
        else:
            current_dt = current_dt.replace(month=month + 1)
    
    return total_records

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MTA Subway Data Ingestion to GCS')
    parser.add_argument('--test', action='store_true', help='Run in test mode with limited records')
    parser.add_argument('--test-limit', type=int, default=100, help='Number of records to fetch in test mode')
    args = parser.parse_args()

    # Process and save 2020-2024 dataset
    print("\nProcessing 2020-2024 dataset...")
    total_2020_2024 = process_and_save_monthly(
        MTA_2020_2024_URL,
        START_DATE,
        "2025-01-01T00:00:00.000",
        args.test,
        args.test_limit
    )

    # Process and save 2025 dataset
    print("\nProcessing 2025 dataset...")
    total_2025 = process_and_save_monthly(
        MTA_2025_URL,
        "2025-01-01T00:00:00.000",
        END_DATE,
        args.test,
        args.test_limit
    )

    print(f"\nTotal records processed: {total_2020_2024 + total_2025}") 