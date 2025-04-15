import os
import dlt
import requests
import argparse
from datetime import datetime
from dotenv import load_dotenv
from typing import Iterator, Dict, List
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Constants
MTA_2020_2024_URL = "https://data.ny.gov/resource/wujg-7c2s.json"
MTA_2025_URL = "https://data.ny.gov/resource/5wq4-mkjj.json"
API_TOKEN = os.getenv('MTA_API_TOKEN')
PAGE_SIZE = 1000
START_DATE = "2023-01-01T00:00:00.000"
END_DATE = "2025-04-01T00:00:00.000"

def fetch_data_from_url(url: str, start_date: str, end_date: str, limit: int = PAGE_SIZE, test_mode: bool = False) -> Iterator[Dict]:
    """
    Fetch MTA subway ridership data with pagination from a specific URL.
    """
    offset = 0
    total_records = 0
    pbar = None
    if test_mode:
        pbar = tqdm(total=limit, desc=f"Fetching from {url}")
    while True:
        if test_mode and total_records >= limit:
            print("Test mode: Reached limit of records to fetch")
            break
        print(f"Fetching records {offset} to {offset + limit} from {url}...")
        params = {
            "$limit": limit,
            "$offset": offset,
            "$where": f"transit_timestamp >= '{start_date}' AND transit_timestamp < '{end_date}'",
            "$$app_token": API_TOKEN
        }
        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                break
            for record in data:
                yield record
                total_records += 1
                if pbar:
                    pbar.update(1)
                if test_mode and total_records >= limit:
                    break
            if test_mode and total_records >= limit:
                break
            offset += limit
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            break
    if pbar:
        pbar.close()

@dlt.source
def mta_source(test_mode: bool = False, test_limit: int = 100):
    """
    dlt source that yields MTA subway ridership data from both datasets.
    """
    # Fetch data from 2020-2024 dataset
    data_2020_2024 = fetch_data_from_url(
        MTA_2020_2024_URL,
        START_DATE,
        "2025-01-01T00:00:00.000",
        PAGE_SIZE,
        test_mode
    )
    
    # Fetch data from 2025 dataset
    data_2025 = fetch_data_from_url(
        MTA_2025_URL,
        "2025-01-01T00:00:00.000",
        END_DATE,
        PAGE_SIZE,
        test_mode
    )
    
    # Combine both data sources
    combined_data = []
    for record in data_2020_2024:
        combined_data.append(record)
    for record in data_2025:
        combined_data.append(record)
        
    return dlt.resource(combined_data, name="mta_subway_ridership")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MTA Subway Data Ingestion Pipeline')
    parser.add_argument('--test', action='store_true', help='Run in test mode with limited records')
    parser.add_argument('--test-limit', type=int, default=100, help='Number of records to fetch in test mode')
    args = parser.parse_args()

    # Create the pipeline to load into BigQuery
    pipeline = dlt.pipeline(
        pipeline_name="mta_subway_pipeline",
        destination="bigquery",
        dataset_name=os.getenv('GCP_DATASET_ID')
    )

    # Run pipeline
    load_info = pipeline.run(mta_source(test_mode=args.test, test_limit=args.test_limit))
    print(load_info) 