from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SystemRoleDefinition:
    """Canonical tenant system-role definition."""

    role_code: str
    role_name: str
    description: str
    permission_codes: tuple[str, ...]


SYSTEM_ROLE_CATALOG: tuple[SystemRoleDefinition, ...] = (
    SystemRoleDefinition(
        role_code="TENANT_ADMIN",
        role_name="Tenant Administrator",
        description="Full tenant administration and engineering access.",
        permission_codes=(
            "organization.read",
            "organization.manage",
            "user.read",
            "user.manage",
            "role.read",
            "role.manage",
            "project.read",
            "project.write",
            "engineering.calculate",
            "assessment.read",
            "assessment.write",
            "report.read",
            "report.export",
            "standards.read",
        ),
    ),
    SystemRoleDefinition(
        role_code="ENGINEER",
        role_name="Engineer",
        description="Engineering project, calculation, assessment, and report access.",
        permission_codes=(
            "organization.read",
            "user.read",
            "role.read",
            "project.read",
            "project.write",
            "engineering.calculate",
            "assessment.read",
            "assessment.write",
            "report.read",
            "report.export",
            "standards.read",
        ),
    ),
    SystemRoleDefinition(
        role_code="REVIEWER",
        role_name="Engineering Reviewer",
        description="Read and review engineering projects, assessments, and reports.",
        permission_codes=(
            "organization.read",
            "project.read",
            "assessment.read",
            "report.read",
            "standards.read",
        ),
    ),
    SystemRoleDefinition(
        role_code="VIEWER",
        role_name="Viewer",
        description="Read-only access to approved engineering information.",
        permission_codes=(
            "organization.read",
            "project.read",
            "assessment.read",
            "report.read",
            "standards.read",
        ),
    ),
)


def get_system_role_definition(
    role_code: str,
) -> SystemRoleDefinition | None:
    """Return a canonical system-role definition by code."""

    normalized_code = role_code.strip().upper()

    for role in SYSTEM_ROLE_CATALOG:
        if role.role_code == normalized_code:
            return role

    return None
