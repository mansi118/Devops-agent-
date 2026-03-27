resource "aws_security_group" "monitoring" {
  name_prefix = "ops-neop-monitoring-${var.environment}-"
  vpc_id      = var.vpc_id
  description = "Security group for Ops NEop monitoring stack"

  ingress {
    description = "Prometheus"
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  ingress {
    description = "Grafana"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  ingress {
    description = "Node Exporter"
    from_port   = 9100
    to_port     = 9100
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "ops-neop-monitoring-${var.environment}" }
}

variable "environment" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }
variable "grafana_password" { type = string; sensitive = true }

output "security_group_id" { value = aws_security_group.monitoring.id }
output "grafana_url" { value = "http://localhost:3000" }
