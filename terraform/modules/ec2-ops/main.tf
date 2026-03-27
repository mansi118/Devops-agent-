data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
}

resource "aws_iam_role" "ops_agent" {
  name = "ops-neop-agent-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "ops_agent" {
  name = "ops-neop-agent-policy"
  role = aws_iam_role.ops_agent.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchCheckLayerAvailability"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
        Resource = [var.s3_bucket_arn, "${var.s3_bucket_arn}/*"]
      },
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = [for arn in values(var.secrets_arns) : arn]
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricData",
          "cloudwatch:ListMetrics",
          "cloudwatch:PutMetricData",
          "logs:GetLogEvents",
          "logs:FilterLogEvents"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeVolumes",
          "ec2:DescribeSecurityGroups",
          "rds:DescribeDBInstances"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ops_agent" {
  name = "ops-neop-agent-${var.environment}"
  role = aws_iam_role.ops_agent.name
}

resource "aws_security_group" "ops_agent" {
  name_prefix = "ops-neop-agent-${var.environment}-"
  vpc_id      = var.vpc_id
  description = "Security group for Ops NEop agent"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  ingress {
    description = "Stakpak MCP"
    from_port   = 8765
    to_port     = 8765
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  ingress {
    description = "Slack Bot Health"
    from_port   = 3001
    to_port     = 3001
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "ops-neop-agent-${var.environment}" }
}

resource "aws_instance" "ops_agent" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_pair_name
  subnet_id              = var.subnet_id
  iam_instance_profile   = aws_iam_instance_profile.ops_agent.name
  vpc_security_group_ids = [aws_security_group.ops_agent.id]

  root_block_device {
    volume_size = 50
    volume_type = "gp3"
    encrypted   = true
  }

  user_data = <<-EOF
    #!/bin/bash
    set -euo pipefail

    # Install Docker
    apt-get update
    apt-get install -y docker.io docker-compose-v2 curl jq git
    systemctl enable docker
    systemctl start docker
    usermod -aG docker ubuntu

    # Install Stakpak
    curl -sSL https://stakpak.dev/install.sh | sh

    # Create ops user
    useradd -m -s /bin/bash -G docker ops
    mkdir -p /opt/ops-neop /var/log/ops-neop
    chown ops:ops /opt/ops-neop /var/log/ops-neop

    echo "Ops NEop EC2 setup complete"
  EOF

  tags = { Name = "ops-neop-agent-${var.environment}" }
}

variable "environment" { type = string }
variable "instance_type" { type = string; default = "t3.medium" }
variable "vpc_id" { type = string }
variable "subnet_id" { type = string }
variable "key_pair_name" { type = string }
variable "ecr_repository_url" { type = string }
variable "s3_bucket_arn" { type = string }
variable "secrets_arns" { type = map(string) }

output "instance_id" { value = aws_instance.ops_agent.id }
output "public_ip" { value = aws_instance.ops_agent.public_ip }
