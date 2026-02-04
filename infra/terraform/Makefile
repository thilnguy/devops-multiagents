# DevOps Multi-Agent Terraform Makefile
# Ensures correct -var-file is always used for each environment

.PHONY: init plan-dev plan-staging plan-prod apply validate clean

# Var files
NONPROD_VARS = terraform.nonprod.tfvars
PROD_VARS = terraform.prod.tfvars

# Default target
help:
	@echo "Available targets:"
	@echo "  init          - Initialize Terraform"
	@echo "  plan-dev      - Plan for Dev environment (uses nonprod vars)"
	@echo "  plan-staging  - Plan for Staging environment (uses nonprod vars)"
	@echo "  plan-prod     - Plan for Production environment (uses prod vars)"
	@echo "  apply         - Apply the saved plan (tfplan)"
	@echo "  validate      - Run policy validation on current plan"
	@echo "  clean         - Remove generated files"

init:
	terraform init

plan-dev: init
	terraform plan -var-file=$(NONPROD_VARS) -out=tfplan
	@echo "✅ Plan for DEV created. Run 'make validate' then 'make apply'."

plan-staging: init
	terraform plan -var-file=$(NONPROD_VARS) -out=tfplan
	@echo "✅ Plan for STAGING created. Run 'make validate' then 'make apply'."

plan-prod: init
	terraform plan -var-file=$(PROD_VARS) -out=tfplan
	@echo "✅ Plan for PRODUCTION created. Run 'make validate' then 'make apply'."

validate:
	terraform show -json tfplan > tfplan.json
	python3 ../../tests/scripts/validate_infra_policies.py tfplan.json --env $(ENV)
	@echo "✅ Policy validation passed!"

apply:
	terraform apply tfplan

clean:
	rm -f tfplan tfplan.json
	rm -rf .terraform
