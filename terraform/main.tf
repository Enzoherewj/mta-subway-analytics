terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
  backend "local" {} # Can be changed to GCS backend in production
}

provider "google" {
  project     = var.project_id
  region      = var.region
  credentials = file(var.credentials_file)  # Use the service account JSON file
}

# Create GCS Bucket for data lake
resource "google_storage_bucket" "mta_data_lake" {
  name          = "${var.project_id}-mta-data-lake"
  location      = var.region
  force_destroy = true  # Allows bucket to be deleted even if not empty

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 30  # days
    }
    action {
      type = "Delete"
    }
  }
}

# Create BigQuery Dataset
resource "google_bigquery_dataset" "mta_data" {
  dataset_id  = "mta_subway_data"
  description = "Dataset for MTA Subway ridership analytics"
  location    = var.region

  # Optional: Set default table expiration
  default_table_expiration_ms = 2592000000 # 30 days
}

# Note: For multi-region, set var.region to "US" in terraform.tfvars 