terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }

  backend "s3" {
    bucket         = "neuraledge-terraform-state"
    key            = "ops-neop/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "ops-neop"
      Environment = var.environment
      ManagedBy   = "terraform"
      Team        = "neuraledge"
    }
  }
}

module "ecr" {
  source          = "./modules/ecr"
  repository_name = "ops-neop"
  environment     = var.environment
}

module "s3_artifacts" {
  source               = "./modules/s3-artifacts"
  environment          = var.environment
  audit_retention_days = 365
  cache_retention_days = 30
}

module "secrets" {
  source      = "./modules/secrets"
  environment = var.environment
  secret_names = [
    "anthropic-api-key",
    "github-token",
    "slack-bot-token",
    "slack-app-token",
    "stakpak-api-key",
    "convex-api-key",
    "snyk-api-token",
    "grafana-api-key",
  ]
}

module "monitoring" {
  source           = "./modules/monitoring"
  environment      = var.environment
  vpc_id           = var.vpc_id
  subnet_ids       = var.subnet_ids
  grafana_password = var.grafana_password
}

module "ec2_ops" {
  source             = "./modules/ec2-ops"
  environment        = var.environment
  instance_type      = var.ops_instance_type
  vpc_id             = var.vpc_id
  subnet_id          = var.subnet_ids[0]
  key_pair_name      = var.key_pair_name
  ecr_repository_url = module.ecr.repository_url
  s3_bucket_arn      = module.s3_artifacts.bucket_arn
  secrets_arns       = module.secrets.secret_arns
}
