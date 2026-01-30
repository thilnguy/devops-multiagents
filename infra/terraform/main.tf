# DevOps Multi-Agent Ecosystem - Terraform Configuration
# This provides a sample infrastructure setup for testing the ecosystem.

terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Provider configuration - update with your credentials
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "devops-multiagents"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# VPC Module - Example infrastructure
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-vpc"
  cidr = var.vpc_cidr

  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs

  enable_nat_gateway = true
  single_nat_gateway = var.environment != "production"

  tags = {
    Terraform   = "true"
    Environment = var.environment
  }
}

# Output for other modules
output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}

output "private_subnets" {
  description = "List of private subnet IDs"
  value       = module.vpc.private_subnets
}
