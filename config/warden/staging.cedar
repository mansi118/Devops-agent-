// ============================================================
// Ops NEop — Staging Environment Guardrail Policies
// More permissive — allows auto-deployment and testing
// ============================================================

// ALLOW: Auto-deploy to staging without approval
permit (principal, action == "deploy", resource)
when {
    resource.target == "staging" &&
    resource.profile == "deploy" &&
    resource.tests_passed == true &&
    resource.security_scan_passed == true
};

// ALLOW: Service restart in staging
permit (principal, action == "restart_service", resource)
when {
    resource.target == "staging"
};

// ALLOW: Run tests in staging
permit (principal, action == "execute_command", resource)
when {
    resource.target == "staging" && (
        resource.command.contains("pytest") ||
        resource.command.contains("jest") ||
        resource.command.contains("npm test") ||
        resource.command.contains("cargo test")
    )
};

// BLOCK: Destructive staging operations still need care
forbid (principal, action == "execute_command", resource)
when {
    resource.target == "staging" && (
        resource.command.contains("terraform destroy") ||
        resource.command.contains("DROP DATABASE")
    )
} unless {
    resource.has_approval == true
};

// ALLOW: Docker operations in staging
permit (principal, action == "execute_command", resource)
when {
    resource.target == "staging" && (
        resource.command.contains("docker") ||
        resource.command.contains("docker-compose")
    )
};

// RATE LIMIT: Max 20 staging deployments per day
forbid (principal, action == "deploy", resource)
when {
    resource.target == "staging" &&
    resource.daily_deploy_count >= 20
};
