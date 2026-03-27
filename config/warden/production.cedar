// ============================================================
// Ops NEop — Production Environment Guardrail Policies
// Strictest guardrails — everything requires approval
// ============================================================

// BLOCK: All production changes without explicit approval
forbid (principal, action == "execute_command", resource)
when {
    resource.target == "production" &&
    resource.profile != "incident"
} unless {
    resource.has_approval == true &&
    resource.approval_source == "slack" &&
    resource.approval_age_minutes < 30
};

// BLOCK: Production deployment without canary passing
forbid (principal, action == "deploy", resource)
when {
    resource.target == "production" &&
    resource.strategy != "canary"
} unless {
    resource.canary_passed == true &&
    resource.canary_pass_age_minutes < 60
};

// BLOCK: Destructive infrastructure operations
forbid (principal, action == "execute_command", resource)
when {
    resource.target == "production" && (
        resource.command.contains("terraform destroy") ||
        resource.command.contains("kubectl delete namespace") ||
        resource.command.contains("kubectl delete deployment") ||
        resource.command.contains("aws ec2 terminate-instances") ||
        resource.command.contains("aws rds delete") ||
        resource.command.contains("aws s3 rb")
    )
} unless {
    resource.has_approval == true &&
    resource.approval_source == "slack" &&
    resource.approver_role == "admin" &&
    resource.approval_age_minutes < 15
};

// BLOCK: Direct SSH to production
forbid (principal, action == "execute_command", resource)
when {
    resource.target == "production" &&
    resource.command.contains("ssh")
};

// BLOCK: Database direct access in production
forbid (principal, action == "execute_command", resource)
when {
    resource.target == "production" && (
        resource.command.contains("psql") ||
        resource.command.contains("mysql") ||
        resource.command.contains("mongo") ||
        resource.command.contains("redis-cli")
    )
};

// ALLOW: Production rollback during incidents (with audit)
permit (principal, action == "rollback", resource)
when {
    resource.target == "production" &&
    resource.profile == "incident" &&
    resource.incident_severity == "P1"
} advice {
    audit_level = "verbose",
    notify = ["#ops-alerts", "ml", "shivam"]
};

// ALLOW: Production health checks (read-only)
permit (principal, action == "health_check", resource)
when {
    resource.target == "production"
};

// RATE LIMIT: Max 3 production deployments per day
forbid (principal, action == "deploy", resource)
when {
    resource.target == "production" &&
    resource.daily_deploy_count >= 3
};
