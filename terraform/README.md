# MTA Subway Analytics Infrastructure

This directory contains Terraform configurations to set up the GCP infrastructure for the MTA Subway Analytics project.

## Prerequisites

1. Install [Terraform](https://www.terraform.io/downloads.html)
2. Have a GCP project created

## Manual Setup (Required Before Running Terraform)

1. Create a service account in GCP Console:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Name it "terraform-admin"
   - Grant these roles:
     - BigQuery Admin
     - Storage Admin
     - Project IAM Admin

2. Create and download a key for this service account:
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose JSON format
   - Save the key file securely

3. Set the environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/terraform-service-account-key.json"
```

## Configuration

1. Copy the example variables file:
```bash
cp terraform.tfvars.example terraform.tfvars
```

2. Edit `terraform.tfvars` with your values:
```hcl
project_id = "your-project-id"
region     = "us-central1"
zone       = "us-central1-a"
```

## Usage

1. Initialize Terraform:
```bash
terraform init
```

2. Review the planned changes:
```bash
terraform plan
```

3. Apply the configuration:
```bash
terraform apply
```

## Infrastructure Created

- GCS bucket for data lake
- BigQuery dataset

## Security Notes

- Keep your service account key secure and never commit it to version control
- The GCS bucket has versioning enabled and a 30-day lifecycle rule 