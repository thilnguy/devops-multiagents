# CloudTrail Configuration for Terraform Audit Logging
# Tracks all API calls made by Terraform for security and compliance

# -----------------------------------------------------------------------------
# CloudTrail S3 Bucket for Logs
# -----------------------------------------------------------------------------
resource "aws_s3_bucket" "cloudtrail_logs" {
  count = var.enable_audit_logging ? 1 : 0

  bucket = "${local.name_prefix}-cloudtrail-logs"

  tags = merge(local.common_tags, {
    Purpose = "audit-logging"
  })
}

resource "aws_s3_bucket_policy" "cloudtrail_logs" {
  count = var.enable_audit_logging ? 1 : 0

  bucket = aws_s3_bucket.cloudtrail_logs[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail_logs[0].arn
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail_logs[0].arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

resource "aws_s3_bucket_lifecycle_configuration" "cloudtrail_logs" {
  count = var.enable_audit_logging ? 1 : 0

  bucket = aws_s3_bucket.cloudtrail_logs[0].id

  rule {
    id     = "archive-old-logs"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}

# -----------------------------------------------------------------------------
# CloudTrail for Terraform API Auditing
# -----------------------------------------------------------------------------
resource "aws_cloudtrail" "terraform_audit" {
  count = var.enable_audit_logging ? 1 : 0

  name                          = "${local.name_prefix}-terraform-audit"
  s3_bucket_name                = aws_s3_bucket.cloudtrail_logs[0].bucket
  include_global_service_events = true
  is_multi_region_trail         = false  # Single region for cost savings
  enable_logging                = true

  # Event selectors for management events
  event_selector {
    read_write_type           = "All"
    include_management_events = true
  }

  tags = merge(local.common_tags, {
    Purpose = "terraform-audit"
  })

  depends_on = [aws_s3_bucket_policy.cloudtrail_logs]
}

# -----------------------------------------------------------------------------
# CloudWatch Log Group for Real-time Alerts (Optional)
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_log_group" "cloudtrail" {
  count = var.enable_audit_logging && var.environment == "production" ? 1 : 0

  name              = "/aws/cloudtrail/${local.name_prefix}"
  retention_in_days = 30

  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# Outputs
# -----------------------------------------------------------------------------
output "cloudtrail_arn" {
  description = "CloudTrail ARN for terraform audit"
  value       = var.enable_audit_logging ? aws_cloudtrail.terraform_audit[0].arn : null
}

output "cloudtrail_logs_bucket" {
  description = "S3 bucket for CloudTrail logs"
  value       = var.enable_audit_logging ? aws_s3_bucket.cloudtrail_logs[0].bucket : null
}
