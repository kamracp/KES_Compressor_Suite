from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PermissionDefinition:
    """Canonical SaaS permission definition."""

    permission_code: str
    permission_name: str
    resource: str
    action: str
    description: str


PERMISSION_CATALOG: tuple[PermissionDefinition, ...] = (
    PermissionDefinition(
        permission_code="organization.read",
        permission_name="Read organizations",
        resource="organization",
        action="read",
        description="View tenant organization information.",
    ),
    PermissionDefinition(
        permission_code="organization.manage",
        permission_name="Manage organizations",
        resource="organization",
        action="manage",
        description="Create and update tenant organization settings.",
    ),
    PermissionDefinition(
        permission_code="user.read",
        permission_name="Read users",
        resource="user",
        action="read",
        description="View tenant user accounts.",
    ),
    PermissionDefinition(
        permission_code="user.manage",
        permission_name="Manage users",
        resource="user",
        action="manage",
        description="Create and update tenant user accounts.",
    ),
    PermissionDefinition(
        permission_code="role.read",
        permission_name="Read roles",
        resource="role",
        action="read",
        description="View tenant roles and assigned permissions.",
    ),
    PermissionDefinition(
        permission_code="role.manage",
        permission_name="Manage roles",
        resource="role",
        action="manage",
        description="Create roles and assign roles or permissions.",
    ),
    PermissionDefinition(
        permission_code="project.read",
        permission_name="Read projects",
        resource="project",
        action="read",
        description="View compressor engineering projects.",
    ),
    PermissionDefinition(
        permission_code="project.write",
        permission_name="Modify projects",
        resource="project",
        action="write",
        description="Create and update compressor engineering projects.",
    ),
    PermissionDefinition(
        permission_code="engineering.calculate",
        permission_name="Run engineering calculations",
        resource="engineering",
        action="calculate",
        description="Execute compressor and compressed-air calculations.",
    ),
    PermissionDefinition(
        permission_code="assessment.read",
        permission_name="Read assessments",
        resource="assessment",
        action="read",
        description="View engineering assessment results.",
    ),
    PermissionDefinition(
        permission_code="assessment.write",
        permission_name="Modify assessments",
        resource="assessment",
        action="write",
        description="Create and update engineering assessments.",
    ),
    PermissionDefinition(
        permission_code="report.read",
        permission_name="Read reports",
        resource="report",
        action="read",
        description="View generated engineering reports.",
    ),
    PermissionDefinition(
        permission_code="report.export",
        permission_name="Export reports",
        resource="report",
        action="export",
        description="Export engineering reports and deliverables.",
    ),
    PermissionDefinition(
        permission_code="standards.read",
        permission_name="Read standards",
        resource="standards",
        action="read",
        description="View engineering standards and compliance mappings.",
    ),
)


def get_permission_definition(
    permission_code: str,
) -> PermissionDefinition | None:
    """Return a canonical permission definition by code."""

    normalized_code = permission_code.strip().lower()

    for permission in PERMISSION_CATALOG:
        if permission.permission_code == normalized_code:
            return permission

    return None
