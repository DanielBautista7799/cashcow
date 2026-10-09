from decimal import Decimal

from app.models.atm import Atm
from app.models.enums import (
    AtmStatus,
    ServiceCallPriority,
    ServiceCallStatus,
)
from app.models.service_call import ServiceCall
from fastapi import HTTPException
from app.main import healthready
import asyncio

def make_atm(
    cash_level: Decimal,
    status: AtmStatus = AtmStatus.OPERATIONAL,
) -> Atm:
    # Small factory avoids repeating the same atm setup in every test
    return Atm(
        serial_number="TEST-ATM",
        model="TEST-MODEL",
        status=status,
        cash_level=cash_level,
        branch_id=1,
    )


def test_atm_under_20_percent_is_low_cash():
    atm = make_atm(Decimal("19.99"))

    assert atm.is_low_cash() is True


def test_atm_at_20_percent_is_not_low_cash():
    atm = make_atm(Decimal("20.00"))

    assert atm.is_low_cash() is False


def test_atm_in_maintenance_needs_maintenance():
    atm = make_atm(
        Decimal("80.00"),
        status=AtmStatus.MAINTENANCE,
    )

    assert atm.needs_maintenance() is True


def test_operational_atm_does_not_need_maintenance():
    atm = make_atm(
        Decimal("80.00"),
        status=AtmStatus.OPERATIONAL,
    )

    assert atm.needs_maintenance() is False


def test_service_call_can_be_marked_completed():
    service_call = ServiceCall(
        title="Test Service Call",
        priority=ServiceCallPriority.MEDIUM,
        status=ServiceCallStatus.IN_PROGRESS,
        atm_id=1,
        technician_id=1,
    )

    service_call.mark_completed()

    assert (
        service_call.status
        == ServiceCallStatus.COMPLETED
    )


def test_service_call_can_be_marked_failed():
    service_call = ServiceCall(
        title="Test Service Call",
        priority=ServiceCallPriority.CRITICAL,
        status=ServiceCallStatus.IN_PROGRESS,
        atm_id=1,
        technician_id=1,
    )

    service_call.mark_failed()

    assert (
        service_call.status
        == ServiceCallStatus.FAILED
    )

def test_health_ready_returns_503_when_database_unavailable():
    class BrokenDB:
        async def execute(self, statement):
            raise Exception("Database unavailable")

    async def run_test():
        try:
            await healthready(BrokenDB())
            assert False
        except HTTPException as error:
            assert error.status_code == 503
            assert error.detail == "Database unavailable"

    asyncio.run(run_test())