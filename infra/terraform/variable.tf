# DevOps Multi-Agent Ecosystem - Terraform Variables
# Production-ready variable definitions with validation

# -----------------------------------------------------------------------------
# Core Configuration
# -----------------------------------------------------------------------------
variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "eu-west-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]$", var.aws_region))
    error_message = "AWS region must be a valid region format (e.g., eu-west-1)."
  }
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be one of: dev, staging, production."
  }
}

variable "project_name" {
  description = "Project name for resource naming (alphanumeric and hyphens only)"
  type        = string
  default     = "devops-multiagents"

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Project name must contain only lowercase letters, numbers, and hyphens."
  }
}

# -----------------------------------------------------------------------------
# Network Configuration
# -----------------------------------------------------------------------------
variable "vpc_cidr" {
  description = "CIDR block for VPC (must be /16 to /24)"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid CIDR block."
  }
}

variable "availability_zones" {
  description = "List of availability zones (leave empty for auto-discovery)"
  type        = list(string)
  default     = []
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets (must be within VPC CIDR)"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]

  validation {
    condition     = length(var.private_subnet_cidrs) >= 2
    error_message = "At least 2 private subnets are required for high availability."
  }
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets (must be within VPC CIDR)"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]

  validation {
    condition     = length(var.public_subnet_cidrs) >= 2
    error_message = "At least 2 public subnets are required for high availability."
  }
}

# -----------------------------------------------------------------------------
# Optional Features
# -----------------------------------------------------------------------------
variable "enable_flow_logs" {
  description = "Enable VPC flow logs (recommended for production)"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Additional tags for all resources"
  type        = map(string)
  default     = {}
}

# -----------------------------------------------------------------------------
# EKS Configuration
# -----------------------------------------------------------------------------
variable "eks_cluster_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.29"
}

variable "eks_node_group_instance_types" {
  description = "Instance types for EKS managed node groups"
  type        = list(string)
  default     = ["t4g.medium"] # ARM64 by default for cost savings
}

variable "eks_node_group_capacity_type" {
  description = "Capacity type for EKS managed node groups (ON_DEMAND or SPOT)"
  type        = string
  default     = "SPOT" # Default to Spot for maximum savings

  validation {
    condition     = contains(["ON_DEMAND", "SPOT"], var.eks_node_group_capacity_type)
    error_message = "Capacity type must be ON_DEMAND or SPOT."
  }
}

variable "eks_node_group_scaling_config" {
  description = "Scaling configuration for EKS managed node groups"
  type = object({
    desired_size = number
    max_size     = number
    min_size     = number
  })
  default = {
    desired_size = 2
    max_size     = 3
    min_size     = 1
  }
}

variable "enable_cluster_creator_admin_permissions" {
  description = "Indicates whether or not to add the cluster creator (the identity used by Terraform) as an administrator via Access Entry"
  type        = bool
  default     = true
}

# -----------------------------------------------------------------------------
# RDS Configuration
# -----------------------------------------------------------------------------
variable "enable_rds" {
  description = "Enable RDS database deployment"
  type        = bool
  default     = false # Disabled by default for demo
}

variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro" # ARM64 Graviton, smallest for demo
}

variable "rds_allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
  default     = 20
}

variable "rds_max_allocated_storage" {
  description = "Max allocated storage for autoscaling in GB"
  type        = number
  default     = 100
}

variable "rds_db_name" {
  description = "Database name"
  type        = string
  default     = "devops_agents"
}

variable "rds_username" {
  description = "Database master username"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "rds_password" {
  description = "Database master password (use secrets manager in production)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "rds_multi_az" {
  description = "Enable Multi-AZ for high availability (adds ~$50/mo)"
  type        = bool
  default     = false # Use Cross-Region Backup instead for demo
}

variable "rds_backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

variable "enable_cross_region_backup" {
  description = "Enable Cross-Region Backup replication for DR (~$5/mo)"
  type        = bool
  default     = true # Cheaper DR option
}

# -----------------------------------------------------------------------------
# Security & Audit Configuration
# -----------------------------------------------------------------------------
variable "enable_audit_logging" {
  description = "Enable CloudTrail audit logging for Terraform API calls"
  type        = bool
  default     = false # Enable in production
}
