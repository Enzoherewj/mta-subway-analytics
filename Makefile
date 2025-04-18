.PHONY: init-infra apply-infra ingest transform test clean load-bq

# Infrastructure
init-infra:
	cd terraform && terraform init

apply-infra:
	cd terraform && terraform apply

destroy-infra:
	cd terraform && terraform destroy

# Data Pipeline
ingest:
	python data_ingestion/mta_ingest.py

ingest-test:
	python data_ingestion/mta_ingest.py --test --test-limit 100

load-bq:
	python data_ingestion/bq_load.py --all-years

load-bq-test:
	python data_ingestion/bq_load.py --year 2023 --month 1

transform:
	cd dbt && dbt run

test:
	cd dbt && dbt test

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete

# Convenience targets
setup: init-infra apply-infra

pipeline: ingest load-bq transform

all: setup pipeline 