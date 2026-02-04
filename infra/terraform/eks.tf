module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "${local.name_prefix}-cluster"
  cluster_version = var.eks_cluster_version

  cluster_endpoint_public_access = true

  # Networking
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Access Control
  enable_cluster_creator_admin_permissions = var.enable_cluster_creator_admin_permissions

  # Node Groups
  eks_managed_node_groups = {
    main = {
      name = "main-node-group"

      instance_types = var.eks_node_group_instance_types
      capacity_type  = var.eks_node_group_capacity_type

      # Use AL2023 for better performance and ARM64 support
      ami_type = "AL2023_ARM_64_STANDARD"

      min_size     = var.eks_node_group_scaling_config.min_size
      max_size     = var.eks_node_group_scaling_config.max_size
      desired_size = var.eks_node_group_scaling_config.desired_size

      labels = {
        Environment = var.environment
        Project     = var.project_name
      }

      tags = local.common_tags
    }
  }

  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# Kubernetes Provider (Helm/Kubectl)
# -----------------------------------------------------------------------------
# data "aws_eks_cluster_auth" "this" {
#   name = module.eks.cluster_name
# }

# provider "kubernetes" {
#   host                   = module.eks.cluster_endpoint
#   cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
#   token                  = data.aws_eks_cluster_auth.this.token
# }
