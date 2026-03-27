resource "aws_ecr_repository" "ops_neop" {
  name                 = "${var.repository_name}-${var.environment}"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name = "${var.repository_name}-${var.environment}"
  }
}

resource "aws_ecr_lifecycle_policy" "ops_neop" {
  repository = aws_ecr_repository.ops_neop.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 20 tagged images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v", "sha-"]
          countType     = "imageCountMoreThan"
          countNumber   = 20
        }
        action = { type = "expire" }
      },
      {
        rulePriority = 2
        description  = "Expire untagged images after 7 days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 7
        }
        action = { type = "expire" }
      }
    ]
  })
}

variable "repository_name" {
  type = string
}

variable "environment" {
  type = string
}

output "repository_url" {
  value = aws_ecr_repository.ops_neop.repository_url
}

output "repository_arn" {
  value = aws_ecr_repository.ops_neop.arn
}
