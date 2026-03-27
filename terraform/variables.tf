variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Environment name (staging or production)"
  type        = string
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be staging or production."
  }
}

variable "vpc_id" {
  description = "VPC ID for Ops NEop resources"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for Ops NEop resources"
  type        = list(string)
}

variable "key_pair_name" {
  description = "EC2 key pair name for SSH access"
  type        = string
}

variable "ops_instance_type" {
  description = "EC2 instance type for Ops NEop agent"
  type        = string
  default     = "t3.medium"
}

variable "grafana_password" {
  description = "Grafana admin password"
  type        = string
  sensitive   = true
}
