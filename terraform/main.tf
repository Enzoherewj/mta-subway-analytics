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
  project = var.project_id
  region  = var.region
}

# Create GCS Bucket for data lake
resource "google_storage_bucket" "data_lake" {
  name          = "${var.project_id}-datalake"
  location      = var.region
  force_destroy = true

  # Optional: Lifecycle rules for managing data retention
  lifecycle_rule {
    condition {
      age = 30  # days
    }
    action {
      type = "Delete"
    }
  }

  versioning {
    enabled = true
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