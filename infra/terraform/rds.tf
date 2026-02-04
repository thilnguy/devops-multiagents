# RDS Database Configuration
# Production: Cross-Region Backup for DR capability
# Non-Prod: Minimal backup for cost savings

# -----------------------------------------------------------------------------
# DB Subnet Group
# -----------------------------------------------------------------------------
resource "aws_db_subnet_group" "main" {
  count = var.enable_rds ? 1 : 0

  name       = "${local.name_prefix}-db-subnet-group"
  subnet_ids = module.vpc.private_subnets

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-subnet-group"
  })
}

# -----------------------------------------------------------------------------
# RDS Security Group
# -----------------------------------------------------------------------------
resource "aws_security_group" "rds" {
  count = var.enable_rds ? 1 : 0

  name        = "${local.name_prefix}-rds-sg"
  description = "Security group for RDS database"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "PostgreSQL from EKS"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = var.private_subnet_cidrs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-rds-sg"
  })
}

# -----------------------------------------------------------------------------
# Secrets Manager for RDS Credentials (P1 Security Fix)
# -----------------------------------------------------------------------------
resource "aws_secretsmanager_secret" "rds_credentials" {
  count = var.enable_rds ? 1 : 0

  name        = "${local.name_prefix}-rds-credentials"
  description = "RDS database credentials for ${local.name_prefix}"

  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "rds_credentials" {
  count = var.enable_rds ? 1 : 0

  secret_id = aws_secretsmanager_secret.rds_credentials[0].id
  secret_string = jsonencode({
    username = var.rds_username
    password = var.rds_password != "" ? var.rds_password : random_password.rds[0].result
    database = var.rds_db_name
  })
}

resource "random_password" "rds" {
  count = var.enable_rds && var.rds_password == "" ? 1 : 0

  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# -----------------------------------------------------------------------------
# RDS Instance
# -----------------------------------------------------------------------------
resource "aws_db_instance" "main" {
  count = var.enable_rds ? 1 : 0

  identifier = "${local.name_prefix}-db"

  # Engine
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.rds_instance_class

  # Storage
  allocated_storage     = var.rds_allocated_storage
  max_allocated_storage = var.rds_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true

  # Credentials from Secrets Manager
  db_name  = var.rds_db_name
  username = var.rds_username
  password = var.rds_password != "" ? var.rds_password : random_password.rds[0].result

  # Network
  db_subnet_group_name   = aws_db_subnet_group.main[0].name
  vpc_security_group_ids = [aws_security_group.rds[0].id]
  publicly_accessible    = false
  port                   = 5432

  # High Availability
  multi_az = var.rds_multi_az

  # Backup Configuration
  backup_retention_period   = var.rds_backup_retention_days
  backup_window             = "03:00-04:00"
  maintenance_window        = "Mon:04:00-Mon:05:00"
  delete_automated_backups  = false
  skip_final_snapshot       = var.environment != "production"
  final_snapshot_identifier = var.environment == "production" ? "${local.name_prefix}-final-snapshot" : null

  # Performance
  performance_insights_enabled = var.environment == "production"

  # Updates
  auto_minor_version_upgrade  = true
  allow_major_version_upgrade = false
  apply_immediately           = var.environment != "production"

  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# Cross-Region Backup (DR Capability - Cheaper than Multi-AZ)
# -----------------------------------------------------------------------------
resource "aws_db_instance_automated_backups_replication" "cross_region" {
  count = var.enable_rds && var.enable_cross_region_backup ? 1 : 0

  source_db_instance_arn = aws_db_instance.main[0].arn

  # Replicate to different region for DR
  # Note: This is a placeholder - actual replication requires provider alias for target region
  retention_period = var.rds_backup_retention_days

  # KMS key for encryption in target region (optional)
  # kms_key_id = var.cross_region_kms_key_arn
}

# -----------------------------------------------------------------------------
# Outputs
# -----------------------------------------------------------------------------
output "rds_endpoint" {
  description = "RDS database endpoint"
  value       = var.enable_rds ? aws_db_instance.main[0].endpoint : null
}

output "rds_arn" {
  description = "RDS database ARN"
  value       = var.enable_rds ? aws_db_instance.main[0].arn : null
}

output "rds_credentials_secret_arn" {
  description = "Secrets Manager ARN for RDS credentials"
  value       = var.enable_rds ? aws_secretsmanager_secret.rds_credentials[0].arn : null
}
