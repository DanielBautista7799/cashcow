import asyncio
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.database import DATABASE_URL
from app.models.atm import Atm
from app.models.audit_entry import AuditEntry
from app.models.enums import (
    AtmStatus,
    ServiceCallPriority,
    ServiceCallStatus,
    UserRole,
)
from app.models.service_call import ServiceCall
from app.models.user import User
from app.services.operations import (
    create_atm,
    create_service_call,
    restore_atm,
    restore_service_call,
    soft_delete_atm,
    soft_delete_service_call,
    update_atm,
    update_service_call,
    update_service_call_status,
)


test_engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    expire_on_commit=False,
)




async def get_admin(db):
    result = await db.execute(
        select(User).where(
            User.role == UserRole.ADMIN
        )
    )
    return result.scalars().first()


async def get_existing_branch_id(db):
    result = await db.execute(
        select(Atm.branch_id)
        .order_by(Atm.id)
        .limit(1)
    )
    return result.scalar_one()


async def get_existing_technician_id(db):
    result = await db.execute(
        select(ServiceCall.technician_id)
        .order_by(ServiceCall.id)
        .limit(1)
    )
    return result.scalar_one()


async def cleanup_test_records(db):
    # Audit entries intentionally have no mutation API, but tests may
    # remove their own rows directly so repeated test runs stay clean.
    atm_ids = (
        await db.execute(
            select(Atm.id).where(
                Atm.serial_number.like(
                    "AUDIT-TEST-%"
                )
            )
        )
    ).scalars().all()

    service_call_ids = (
        await db.execute(
            select(ServiceCall.id).where(
                ServiceCall.title.like(
                    "AUDIT TEST%"
                )
            )
        )
    ).scalars().all()

    if service_call_ids:
        entries = (
            await db.execute(
                select(AuditEntry).where(
                    AuditEntry.record_type
                    == "service_call",
                    AuditEntry.record_id.in_(
                        service_call_ids
                    ),
                )
            )
        ).scalars().all()

        for entry in entries:
            await db.delete(entry)

        calls = (
            await db.execute(
                select(ServiceCall).where(
                    ServiceCall.id.in_(
                        service_call_ids
                    )
                )
            )
        ).scalars().all()

        for call in calls:
            await db.delete(call)

    if atm_ids:
        entries = (
            await db.execute(
                select(AuditEntry).where(
                    AuditEntry.record_type
                    == "atm",
                    AuditEntry.record_id.in_(
                        atm_ids
                    ),
                )
            )
        ).scalars().all()

        for entry in entries:
            await db.delete(entry)

        atms = (
            await db.execute(
                select(Atm).where(
                    Atm.id.in_(atm_ids)
                )
            )
        ).scalars().all()

        for atm in atms:
            await db.delete(atm)

    await db.commit()


def test_atm_soft_delete_restore_and_audit():
    async def run_test():
        async with TestSessionLocal() as db:
            await cleanup_test_records(db)

            admin = await get_admin(db)
            branch_id = (
                await get_existing_branch_id(db)
            )

            assert admin is not None

            atm = await create_atm(
                db,
                {
                    "serial_number":
                        "AUDIT-TEST-ATM-1",
                    "model":
                        "Audit Test Model",
                    "status":
                        AtmStatus.OPERATIONAL,
                    "cash_level":
                        Decimal("50.00"),
                    "branch_id":
                        branch_id,
                },
                admin,
            )

            atm_id = atm.id

            create_entries = (
                await db.execute(
                    select(AuditEntry).where(
                        AuditEntry.record_type
                        == "atm",
                        AuditEntry.record_id
                        == atm_id,
                        AuditEntry.action
                        == "create",
                    )
                )
            ).scalars().all()

            assert len(create_entries) == 1

            atm = await update_atm(
                db,
                atm,
                {
                    "cash_level":
                        Decimal("35.00")
                },
                admin,
            )

            update_entry = (
                await db.execute(
                    select(AuditEntry).where(
                        AuditEntry.record_type
                        == "atm",
                        AuditEntry.record_id
                        == atm_id,
                        AuditEntry.action
                        == "update",
                    )
                )
            ).scalar_one()

            assert (
                update_entry.changes[
                    "cash_level"
                ]["from"]
                == "50.00"
            )

            assert (
                update_entry.changes[
                    "cash_level"
                ]["to"]
                == "35.00"
            )

            atm = await soft_delete_atm(
                db,
                atm,
                admin,
            )

            assert atm.is_active is False
            assert atm.deleted_at is not None
            assert (
                atm.deleted_by
                == admin.id
            )

            visible_count = (
                await db.execute(
                    select(
                        func.count(Atm.id)
                    ).where(
                        Atm.id == atm_id,
                        Atm.is_active.is_(
                            True
                        ),
                    )
                )
            ).scalar_one()

            assert visible_count == 0

            stored = await db.get(
                Atm,
                atm_id,
            )

            assert stored is not None

            delete_entry = (
                await db.execute(
                    select(AuditEntry).where(
                        AuditEntry.record_type
                        == "atm",
                        AuditEntry.record_id
                        == atm_id,
                        AuditEntry.action
                        == "delete",
                    )
                )
            ).scalar_one()

            assert (
                delete_entry.acting_user_id
                == admin.id
            )

            atm = await restore_atm(
                db,
                stored,
                admin,
            )

            assert atm.is_active is True
            assert atm.deleted_at is None
            assert atm.deleted_by is None

            restore_entry = (
                await db.execute(
                    select(AuditEntry).where(
                        AuditEntry.record_type
                        == "atm",
                        AuditEntry.record_id
                        == atm_id,
                        AuditEntry.action
                        == "restore",
                    )
                )
            ).scalar_one()

            assert restore_entry is not None

            history = (
                await db.execute(
                    select(AuditEntry)
                    .where(
                        AuditEntry.record_type
                        == "atm",
                        AuditEntry.record_id
                        == atm_id,
                    )
                    .order_by(
                        AuditEntry.created_at,
                        AuditEntry.id,
                    )
                )
            ).scalars().all()

            assert [
                entry.action
                for entry in history
            ] == [
                "create",
                "update",
                "delete",
                "restore",
            ]

            await cleanup_test_records(db)

    asyncio.run(run_test())


def test_service_call_soft_delete_restore_and_audit():
    async def run_test():
        async with TestSessionLocal() as db:
            await cleanup_test_records(db)

            admin = await get_admin(db)
            branch_id = (
                await get_existing_branch_id(db)
            )
            technician_id = (
                await get_existing_technician_id(
                    db
                )
            )

            atm = await create_atm(
                db,
                {
                    "serial_number":
                        "AUDIT-TEST-ATM-2",
                    "model":
                        "Audit Test Model",
                    "status":
                        AtmStatus.OPERATIONAL,
                    "cash_level":
                        Decimal("60.00"),
                    "branch_id":
                        branch_id,
                },
                admin,
            )

            service_call = (
                await create_service_call(
                    db,
                    {
                        "title":
                            "AUDIT TEST CALL",
                        "priority":
                            ServiceCallPriority.LOW,
                        "status":
                            ServiceCallStatus.PENDING,
                        "atm_id":
                            atm.id,
                        "technician_id":
                            technician_id,
                    },
                    admin,
                )
            )

            call_id = service_call.id

            service_call = (
                await update_service_call(
                    db,
                    service_call,
                    {
                        "title":
                            "AUDIT TEST CALL UPDATED"
                    },
                    admin,
                )
            )

            service_call = (
                await update_service_call_status(
                    db,
                    service_call,
                    ServiceCallStatus.COMPLETED,
                    admin,
                )
            )

            assert (
                service_call.status
                == ServiceCallStatus.COMPLETED
            )

            service_call = (
                await soft_delete_service_call(
                    db,
                    service_call,
                    admin,
                )
            )

            assert (
                service_call.is_active
                is False
            )

            stored = await db.get(
                ServiceCall,
                call_id,
            )

            assert stored is not None

            # Soft-delete the referenced ATM. The service call keeps
            # its foreign key and the ATM row still resolves.
            atm = await soft_delete_atm(
                db,
                atm,
                admin,
            )

            assert atm.is_active is False

            referenced_atm = await db.get(
                Atm,
                stored.atm_id,
            )

            assert referenced_atm is not None
            assert referenced_atm.is_active is False
            assert stored.atm_id == referenced_atm.id

            service_call = (
                await restore_service_call(
                    db,
                    stored,
                    admin,
                )
            )

            assert (
                service_call.is_active
                is True
            )

            history = (
                await db.execute(
                    select(AuditEntry)
                    .where(
                        AuditEntry.record_type
                        == "service_call",
                        AuditEntry.record_id
                        == call_id,
                    )
                    .order_by(
                        AuditEntry.created_at,
                        AuditEntry.id,
                    )
                )
            ).scalars().all()

            assert [
                entry.action
                for entry in history
            ] == [
                "create",
                "update",
                "status_change",
                "delete",
                "restore",
            ]

            await cleanup_test_records(db)

    asyncio.run(run_test())


def test_no_audit_entry_for_uncommitted_change():
    async def run_test():
        async with TestSessionLocal() as db:
            await cleanup_test_records(db)

            admin = await get_admin(db)
            branch_id = (
                await get_existing_branch_id(db)
            )

            atm = Atm(
                serial_number=
                    "AUDIT-TEST-ROLLBACK",
                model=
                    "Audit Rollback Model",
                status=
                    AtmStatus.OPERATIONAL,
                cash_level=
                    Decimal("70.00"),
                branch_id=
                    branch_id,
            )

            db.add(atm)
            await db.flush()

            entry = AuditEntry(
                record_type="atm",
                record_id=atm.id,
                action="create",
                acting_user_id=admin.id,
                changes={
                    "created": True
                },
            )

            db.add(entry)

            atm_id = atm.id

            await db.rollback()

            atm_count = (
                await db.execute(
                    select(
                        func.count(Atm.id)
                    ).where(
                        Atm.id == atm_id
                    )
                )
            ).scalar_one()

            audit_count = (
                await db.execute(
                    select(
                        func.count(
                            AuditEntry.id
                        )
                    ).where(
                        AuditEntry.record_type
                        == "atm",
                        AuditEntry.record_id
                        == atm_id,
                    )
                )
            ).scalar_one()

            assert atm_count == 0
            assert audit_count == 0

            await cleanup_test_records(db)

    asyncio.run(run_test())


def test_audit_entry_model_has_no_mutation_router():
    # This guards the intentional design: audit history is read-only.
    from pathlib import Path

    router_text = "\n".join(
        path.read_text()
        for path in Path(
            "app/routers"
        ).glob("*.py")
    )

    assert "@router.patch(\"/audit" not in router_text
    assert "@router.put(\"/audit" not in router_text
    assert "@router.delete(\"/audit" not in router_text

