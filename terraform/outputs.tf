output "ecr_repository_url" {
  description = "ECR repository URL for Ops NEop images"
  value       = module.ecr.repository_url
}

output "s3_audit_bucket" {
  description = "S3 bucket for audit logs"
  value       = module.s3_artifacts.audit_bucket_name
}

output "s3_cache_bucket" {
  description = "S3 bucket for build cache"
  value       = module.s3_artifacts.cache_bucket_name
}

output "ops_instance_id" {
  description = "EC2 instance ID for Ops NEop agent"
  value       = module.ec2_ops.instance_id
}

output "ops_instance_public_ip" {
  description = "Public IP of the Ops NEop EC2 instance"
  value       = module.ec2_ops.public_ip
}

output "monitoring_grafana_url" {
  description = "Grafana dashboard URL"
  value       = module.monitoring.grafana_url
}

output "secret_arns" {
  description = "ARNs of created secrets"
  value       = module.secrets.secret_arns
  sensitive   = true
}
