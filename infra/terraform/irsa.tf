# IAM Roles for Service Accounts (IRSA)
# Provides least-privilege AWS access for Kubernetes service accounts
# Security Best Practice: Each agent gets only the permissions it needs

# -----------------------------------------------------------------------------
# OIDC Provider (Required for IRSA)
# Note: EKS module creates this, but we reference it here for IRSA modules
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Infra-Bot Role (Terraform Operations)
# -----------------------------------------------------------------------------
module "irsa_infra_bot" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name = "${local.name_prefix}-infra-bot"

  # Trust policy for the EKS OIDC provider
  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["devops-multiagents:infra-bot"]
    }
  }

  # Permissions for Infra-Bot (Terraform state access)
  role_policy_arns = {
    terraform_state = aws_iam_policy.infra_bot_policy.arn
  }

  tags = local.common_tags
}

resource "aws_iam_policy" "infra_bot_policy" {
  name        = "${local.name_prefix}-infra-bot-policy"
  description = "Policy for Infra-Bot Terraform operations"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "TerraformStateAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::devops-multiagents-tfstate",
          "arn:aws:s3:::devops-multiagents-tfstate/*"
        ]
      },
      {
        Sid    = "TerraformLockAccess"
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem"
        ]
        Resource = "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/devops-multiagents-tflock"
      }
    ]
  })

  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# Watchdog Role (Monitoring & Cost)
# -----------------------------------------------------------------------------
module "irsa_watchdog" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name = "${local.name_prefix}-watchdog"

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["devops-multiagents:watchdog"]
    }
  }

  role_policy_arns = {
    watchdog = aws_iam_policy.watchdog_policy.arn
  }

  tags = local.common_tags
}

resource "aws_iam_policy" "watchdog_policy" {
  name        = "${local.name_prefix}-watchdog-policy"
  description = "Policy for Watchdog monitoring and cost analysis"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "CostExplorerReadOnly"
        Effect = "Allow"
        Action = [
          "ce:GetCostAndUsage",
          "ce:GetCostForecast",
          "ce:GetAnomalies"
        ]
        Resource = "*"
      },
      {
        Sid    = "CloudWatchReadOnly"
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
          "logs:FilterLogEvents",
          "logs:GetLogEvents"
        ]
        Resource = "*"
      }
    ]
  })

  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# Kube-Master Role (K8s Deployments)
# Note: Kube-Master primarily uses in-cluster RBAC, minimal AWS access needed
# -----------------------------------------------------------------------------
module "irsa_kube_master" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name = "${local.name_prefix}-kube-master"

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["devops-multiagents:kube-master"]
    }
  }

  # ECR pull access for deployments
  attach_vpc_cni_policy = false
  role_policy_arns = {
    ecr_read = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  }

  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# Outputs
# -----------------------------------------------------------------------------
output "irsa_infra_bot_role_arn" {
  description = "IAM Role ARN for Infra-Bot service account"
  value       = module.irsa_infra_bot.iam_role_arn
}

output "irsa_watchdog_role_arn" {
  description = "IAM Role ARN for Watchdog service account"
  value       = module.irsa_watchdog.iam_role_arn
}

output "irsa_kube_master_role_arn" {
  description = "IAM Role ARN for Kube-Master service account"
  value       = module.irsa_kube_master.iam_role_arn
}
