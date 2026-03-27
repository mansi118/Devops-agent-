resource "aws_s3_bucket" "audit" {
  bucket = "neuraledge-ops-audit-${var.environment}"

  tags = { Name = "neuraledge-ops-audit-${var.environment}" }
}

resource "aws_s3_bucket_versioning" "audit" {
  bucket = aws_s3_bucket.audit.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "audit" {
  bucket = aws_s3_bucket.audit.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}

resource "aws_s3_bucket_public_access_block" "audit" {
  bucket                  = aws_s3_bucket.audit.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "audit" {
  bucket = aws_s3_bucket.audit.id

  rule {
    id     = "archive-to-glacier"
    status = "Enabled"
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
    expiration { days = var.audit_retention_days }
  }
}

resource "aws_s3_bucket" "cache" {
  bucket = "neuraledge-ops-cache-${var.environment}"

  tags = { Name = "neuraledge-ops-cache-${var.environment}" }
}

resource "aws_s3_bucket_public_access_block" "cache" {
  bucket                  = aws_s3_bucket.cache.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "cache" {
  bucket = aws_s3_bucket.cache.id

  rule {
    id     = "expire-cache"
    status = "Enabled"
    expiration { days = var.cache_retention_days }
  }
}

variable "environment" { type = string }
variable "audit_retention_days" { type = number; default = 365 }
variable "cache_retention_days" { type = number; default = 30 }

output "audit_bucket_name" { value = aws_s3_bucket.audit.id }
output "cache_bucket_name" { value = aws_s3_bucket.cache.id }
output "bucket_arn" { value = aws_s3_bucket.audit.arn }
