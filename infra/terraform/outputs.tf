# DevOps Multi-Agent Ecosystem - Terraform Outputs
# Comprehensive outputs for integration with other systems

# -----------------------------------------------------------------------------
# VPC Outputs
# -----------------------------------------------------------------------------
output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnets" {
  description = "List of private subnet IDs"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of public subnet IDs"
  value       = module.vpc.public_subnets
}

output "nat_gateway_ids" {
  description = "List of NAT Gateway IDs"
  value       = module.vpc.natgw_ids
}

# -----------------------------------------------------------------------------
# Infrastructure Metadata
# -----------------------------------------------------------------------------
output "aws_region" {
  description = "AWS region where infrastructure is deployed"
  value       = data.aws_region.current.name
}

output "aws_account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "availability_zones" {
  description = "Availability zones used"
  value       = local.azs
}

output "environment" {
  description = "Deployment environment"
  value       = var.environment
}

# -----------------------------------------------------------------------------
# Integration Outputs (for K8s/EKS)
# -----------------------------------------------------------------------------
output "private_subnet_cidrs" {
  description = "CIDR blocks of private subnets"
  value       = module.vpc.private_subnets_cidr_blocks
}

output "public_subnet_cidrs" {
  description = "CIDR blocks of public subnets"
  value       = module.vpc.public_subnets_cidr_blocks
}

# -----------------------------------------------------------------------------
# Deployment Info
# -----------------------------------------------------------------------------
output "deployment_info" {
  description = "Deployment information for documentation"
  value = {
    project     = var.project_name
    environment = var.environment
    region      = data.aws_region.current.name
    vpc_id      = module.vpc.vpc_id
  }
}

# -----------------------------------------------------------------------------
# EKS Outputs
# -----------------------------------------------------------------------------
output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ids attached to the cluster control plane"
  value       = module.eks.cluster_security_group_id
}

output "cluster_name" {
  description = "Kubernetes Cluster Name"
  value       = module.eks.cluster_name
}

output "kubectl_config_command" {
  description = "Command to configure kubectl"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}
