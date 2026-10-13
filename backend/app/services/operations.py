from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.atm import Atm
from app.models.service_call import ServiceCall
from app.models.user import User
from app.services.audit import (
    add_audit_entry,
    build_changes,
    json_safe,
)


async def _commit(
    db: AsyncSession,
    record,
):
    try:
        await db.commit()
        await db.refresh(record)
    except Exception:
        await db.rollback()
        raise


async def create_atm(
    db: AsyncSession,
    values: dict,
    actor: User,
) -> Atm:
    atm = Atm(**values)

    db.add(atm)

    try:
        await db.flush()

        add_audit_entry(
            db,
            record_type="atm",
            record_id=atm.id,
            action="create",
            actor=actor,
            changes={
                "created": json_safe(values)
            },
        )

        await db.commit()
        await db.refresh(atm)

        return atm

    except Exception:
        await db.rollback()
        raise


async def update_atm(
    db: AsyncSession,
    atm: Atm,
    values: dict,
    actor: User,
) -> Atm:
    changes = build_changes(
        atm,
        values,
    )

    if not changes:
        return atm

    for field, value in values.items():
        setattr(atm, field, value)

    add_audit_entry(
        db,
        record_type="atm",
        record_id=atm.id,
        action="update",
        actor=actor,
        changes=changes,
    )

    await _commit(db, atm)

    return atm


async def soft_delete_atm(
    db: AsyncSession,
    atm: Atm,
    actor: User,
) -> Atm:
    deleted_at = datetime.now(
        timezone.utc
    )

    changes = {
        "is_active": {
            "from": True,
            "to": False,
        },
        "deleted_at": {
            "from": None,
            "to": deleted_at.isoformat(),
        },
        "deleted_by": {
            "from": None,
            "to": actor.id,
        },
    }

    atm.is_active = False
    atm.deleted_at = deleted_at
    atm.deleted_by = actor.id

    add_audit_entry(
        db,
        record_type="atm",
        record_id=atm.id,
        action="delete",
        actor=actor,
        changes=changes,
    )

    await _commit(db, atm)

    return atm


async def restore_atm(
    db: AsyncSession,
    atm: Atm,
    actor: User,
) -> Atm:
    changes = {
        "is_active": {
            "from": False,
            "to": True,
        },
        "deleted_at": {
            "from": json_safe(
                atm.deleted_at
            ),
            "to": None,
        },
        "deleted_by": {
            "from": atm.deleted_by,
            "to": None,
        },
    }

    atm.is_active = True
    atm.deleted_at = None
    atm.deleted_by = None

    add_audit_entry(
        db,
        record_type="atm",
        record_id=atm.id,
        action="restore",
        actor=actor,
        changes=changes,
    )

    await _commit(db, atm)

    return atm


async def create_service_call(
    db: AsyncSession,
    values: dict,
    actor: User,
) -> ServiceCall:
    service_call = ServiceCall(**values)

    db.add(service_call)

    try:
        await db.flush()

        add_audit_entry(
            db,
            record_type="service_call",
            record_id=service_call.id,
            action="create",
            actor=actor,
            changes={
                "created": json_safe(values)
            },
        )

        await db.commit()
        await db.refresh(service_call)

        return service_call

    except Exception:
        await db.rollback()
        raise


async def update_service_call(
    db: AsyncSession,
    service_call: ServiceCall,
    values: dict,
    actor: User,
) -> ServiceCall:
    changes = build_changes(
        service_call,
        values,
    )

    if not changes:
        return service_call

    for field, value in values.items():
        setattr(
            service_call,
            field,
            value,
        )

    add_audit_entry(
        db,
        record_type="service_call",
        record_id=service_call.id,
        action="update",
        actor=actor,
        changes=changes,
    )

    await _commit(
        db,
        service_call,
    )

    return service_call


async def update_service_call_status(
    db: AsyncSession,
    service_call: ServiceCall,
    new_status,
    actor: User,
) -> ServiceCall:
    old_status = service_call.status

    if old_status == new_status:
        return service_call

    if new_status.value == "Completed":
        service_call.mark_completed()

    elif new_status.value == "Failed":
        service_call.mark_failed()

    else:
        service_call.status = new_status

    add_audit_entry(
        db,
        record_type="service_call",
        record_id=service_call.id,
        action="status_change",
        actor=actor,
        changes={
            "status": {
                "from": old_status.value,
                "to": new_status.value,
            }
        },
    )

    await _commit(
        db,
        service_call,
    )

    return service_call


async def soft_delete_service_call(
    db: AsyncSession,
    service_call: ServiceCall,
    actor: User,
) -> ServiceCall:
    deleted_at = datetime.now(
        timezone.utc
    )

    changes = {
        "is_active": {
            "from": True,
            "to": False,
        },
        "deleted_at": {
            "from": None,
            "to": deleted_at.isoformat(),
        },
        "deleted_by": {
            "from": None,
            "to": actor.id,
        },
    }

    service_call.is_active = False
    service_call.deleted_at = deleted_at
    service_call.deleted_by = actor.id

    add_audit_entry(
        db,
        record_type="service_call",
        record_id=service_call.id,
        action="delete",
        actor=actor,
        changes=changes,
    )

    await _commit(
        db,
        service_call,
    )

    return service_call


async def restore_service_call(
    db: AsyncSession,
    service_call: ServiceCall,
    actor: User,
) -> ServiceCall:
    changes = {
        "is_active": {
            "from": False,
            "to": True,
        },
        "deleted_at": {
            "from": json_safe(
                service_call.deleted_at
            ),
            "to": None,
        },
        "deleted_by": {
            "from": service_call.deleted_by,
            "to": None,
        },
    }

    service_call.is_active = True
    service_call.deleted_at = None
    service_call.deleted_by = None

    add_audit_entry(
        db,
        record_type="service_call",
        record_id=service_call.id,
        action="restore",
        actor=actor,
        changes=changes,
    )

    await _commit(
        db,
        service_call,
    )

    return service_call
