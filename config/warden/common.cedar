// ============================================================
// Ops NEop — Common Warden Guardrail Policies
// Applied across ALL profiles
// ============================================================

// BLOCK: Destructive file system operations
forbid (principal, action == "execute_command", resource)
when {
    resource.command.contains("rm -rf /") ||
    resource.command.contains("rm -rf /*") ||
    resource.command.contains("mkfs") ||
    resource.command.contains("> /dev/sda") ||
    resource.command.contains("dd if=/dev/zero") ||
    resource.command.contains("chmod -R 777 /") ||
    resource.command.contains("chown -R") && resource.command.contains("/")
};

// BLOCK: Destructive database operations (unscoped)
forbid (principal, action == "execute_command", resource)
when {
    resource.command.contains("DROP DATABASE") ||
    resource.command.contains("DROP SCHEMA") ||
    (resource.command.contains("DROP TABLE") && !resource.command.contains("IF EXISTS")) ||
    resource.command.contains("TRUNCATE") ||
    (resource.command.contains("DELETE FROM") && !resource.command.contains("WHERE"))
};

// BLOCK: Credential exfiltration attempts
forbid (principal, action == "execute_command", resource)
when {
    resource.command.contains("curl") && resource.command.contains("SECRET") ||
    resource.command.contains("wget") && resource.command.contains("PASSWORD") ||
    resource.command.contains("nc ") && resource.command.contains("SECRET") ||
    resource.command.contains("base64") && resource.command.contains("KEY")
};

// BLOCK: Network reconnaissance (unless in incident profile)
forbid (principal, action == "execute_command", resource)
when {
    resource.command.contains("nmap") ||
    resource.command.contains("masscan") ||
    resource.command.contains("nikto")
} unless {
    resource.profile == "incident"
};

// BLOCK: Cryptocurrency mining
forbid (principal, action == "execute_command", resource)
when {
    resource.command.contains("xmrig") ||
    resource.command.contains("minerd") ||
    resource.command.contains("cryptonight")
};

// REQUIRE: All commands must have a valid profile
forbid (principal, action == "execute_command", resource)
when {
    !resource.has("profile") ||
    resource.profile == ""
};

// AUDIT: Log all commands that modify system state
permit (principal, action == "execute_command", resource)
when {
    resource.command.contains("apt") ||
    resource.command.contains("systemctl") ||
    resource.command.contains("iptables")
} advice {
    audit_level = "verbose"
};
