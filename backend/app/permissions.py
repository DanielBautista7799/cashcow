from enum import Enum

from app.models.enums import UserRole


class Permission(str, Enum):
    SELF_READ = "self:read"

    ASSET_READ = "asset:read"
    ASSET_WRITE = "asset:write"

    JOB_READ = "job:read"
    JOB_WRITE = "job:write"
    JOB_STATUS_WRITE = "job:status"

    REPORT_UPLOAD = "report:upload"

    ANALYTICS_READ = "analytics:read"
    AUDIT_READ = "audit:read"

    USER_MANAGE = "user:manage"


ROLE_PERMISSIONS: dict[UserRole, frozenset[Permission]] = {
    UserRole.ADMIN: frozenset(Permission),

    UserRole.TECHNICIAN: frozenset(
        {
            Permission.SELF_READ,
            Permission.ASSET_READ,
            Permission.JOB_READ,
            Permission.JOB_STATUS_WRITE,
            Permission.REPORT_UPLOAD,
            Permission.ANALYTICS_READ,
            Permission.AUDIT_READ,
        }
    ),

    UserRole.AUDITOR: frozenset(
        {
            Permission.SELF_READ,
            Permission.ASSET_READ,
            Permission.JOB_READ,
            Permission.ANALYTICS_READ,
            Permission.AUDIT_READ,
        }
    ),
}


def permissions_for_role(role: UserRole) -> frozenset[Permission]:
    return ROLE_PERMISSIONS.get(role, frozenset())
