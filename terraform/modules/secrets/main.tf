resource "aws_secretsmanager_secret" "ops_secrets" {
  for_each = toset(var.secret_names)

  name        = "ops-neop/${var.environment}/${each.value}"
  description = "Ops NEop secret: ${each.value} (${var.environment})"

  tags = { Name = "ops-neop-${each.value}" }
}

resource "aws_secretsmanager_secret_version" "ops_secrets" {
  for_each = toset(var.secret_names)

  secret_id     = aws_secretsmanager_secret.ops_secrets[each.value].id
  secret_string = "CHANGE_ME"

  lifecycle { ignore_changes = [secret_string] }
}

variable "environment" { type = string }
variable "secret_names" { type = list(string) }

output "secret_arns" {
  value = { for k, v in aws_secretsmanager_secret.ops_secrets : k => v.arn }
}
