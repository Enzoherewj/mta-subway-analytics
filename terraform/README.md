# Infrastructure as Code

This directory contains Terraform configurations for setting up the GCP infrastructure required for the MTA Subway Analytics pipeline.

## Files

### main.tf
- Defines GCP resources:
  - BigQuery dataset
  - Google Cloud Storage bucket
  - IAM permissions
  - Service accounts

### variables.tf
- Defines input variables:
  - project_id
  - region
  - zone
  - credentials_file

### terraform.tfvars
- Contains actual variable values (not tracked in git)
- Based on terraform.tfvars.example template

### State Files
- terraform.tfstate: Current state
- terraform.tfstate.backup: Backup of previous state
- .terraform.lock.hcl: Dependency lock file

## Setup

1. Copy terraform.tfvars.example to terraform.tfvars:
```bash
cp terraform.tfvars.example terraform.tfvars
```

2. Update terraform.tfvars with your values:
```bash
project_id = "your-project-id"
region     = "US"
zone       = "us-central1-a"
credentials_file = "path/to/your/service-account-key.json"
```

3. Initialize Terraform:
```bash
terraform init
```

## Usage

### Apply Infrastructure
```bash
terraform apply
```

### Destroy Infrastructure
```bash
terraform destroy
```

## Resources Created

- BigQuery Dataset: `mta_subway_analytics`
- GCS Bucket: `mta-subway-data`
- Service Account: `mta-subway-sa`
- IAM Roles:
  - BigQuery Data Editor
  - Storage Object Viewer
  - Storage Object Creator

## Security Notes

- Keep terraform.tfvars and service account keys out of version control
- Use .gitignore to exclude sensitive files
- Rotate service account keys regularly 