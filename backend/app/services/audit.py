from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_entry import AuditEntry
from app.models.user import User


def json_safe(value):
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, Decimal):
        return str(value)

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            key: json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            json_safe(item)
            for item in value
        ]

    return value


def build_changes(
    record,
    values: dict,
) -> dict:
    changes = {}

    for field, new_value in values.items():
        old_value = getattr(record, field)

        if old_value == new_value:
            continue

        changes[field] = {
            "from": json_safe(old_value),
            "to": json_safe(new_value),
        }

    return changes


def add_audit_entry(
    db: AsyncSession,
    *,
    record_type: str,
    record_id: int,
    action: str,
    actor: User,
    changes: dict,
) -> AuditEntry:
    entry = AuditEntry(
        record_type=record_type,
        record_id=record_id,
        action=action,
        acting_user_id=actor.id,
        changes=json_safe(changes),
    )

    db.add(entry)

    return entry
