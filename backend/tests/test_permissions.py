import asyncio

from fastapi import HTTPException

from app.dependencies import require_permission
from app.models.enums import UserRole
from app.permissions import (
    Permission,
    ROLE_PERMISSIONS,
    permissions_for_role,
)


class FakeUser:
    def __init__(self, role):
        self.role = role


def test_admin_has_all_permissions():
    assert permissions_for_role(
        UserRole.ADMIN
    ) == frozenset(Permission)


def test_technician_permissions():
    permissions = permissions_for_role(
        UserRole.TECHNICIAN
    )

    assert Permission.ASSET_READ in permissions
    assert Permission.JOB_READ in permissions
    assert Permission.JOB_STATUS_WRITE in permissions
    assert Permission.REPORT_UPLOAD in permissions
    assert Permission.ANALYTICS_READ in permissions

    assert Permission.ASSET_WRITE not in permissions
    assert Permission.USER_MANAGE not in permissions
    assert Permission.AUDIT_READ in permissions


def test_auditor_permissions():
    permissions = permissions_for_role(
        UserRole.AUDITOR
    )

    assert Permission.ASSET_READ in permissions
    assert Permission.JOB_READ in permissions
    assert Permission.ANALYTICS_READ in permissions
    assert Permission.AUDIT_READ in permissions

    assert Permission.ASSET_WRITE not in permissions
    assert Permission.JOB_STATUS_WRITE not in permissions
    assert Permission.REPORT_UPLOAD not in permissions
    assert Permission.USER_MANAGE not in permissions


def test_admin_can_write_assets():
    async def run_test():
        checker = require_permission(
            Permission.ASSET_WRITE
        )

        user = FakeUser(UserRole.ADMIN)

        result = await checker(
            current_user=user
        )

        assert result is user

    asyncio.run(run_test())


def test_technician_cannot_write_assets():
    async def run_test():
        checker = require_permission(
            Permission.ASSET_WRITE
        )

        user = FakeUser(
            UserRole.TECHNICIAN
        )

        try:
            await checker(
                current_user=user
            )
            assert False
        except HTTPException as error:
            assert error.status_code == 403
            assert (
                error.detail
                == "Missing permission: asset:write"
            )

    asyncio.run(run_test())


def test_auditor_cannot_write_assets():
    async def run_test():
        checker = require_permission(
            Permission.ASSET_WRITE
        )

        user = FakeUser(
            UserRole.AUDITOR
        )

        try:
            await checker(
                current_user=user
            )
            assert False
        except HTTPException as error:
            assert error.status_code == 403
            assert (
                error.detail
                == "Missing permission: asset:write"
            )

    asyncio.run(run_test())


def test_technician_can_change_job_status():
    async def run_test():
        checker = require_permission(
            Permission.JOB_STATUS_WRITE
        )

        user = FakeUser(
            UserRole.TECHNICIAN
        )

        result = await checker(
            current_user=user
        )

        assert result is user

    asyncio.run(run_test())


def test_auditor_cannot_change_job_status():
    async def run_test():
        checker = require_permission(
            Permission.JOB_STATUS_WRITE
        )

        user = FakeUser(
            UserRole.AUDITOR
        )

        try:
            await checker(
                current_user=user
            )
            assert False
        except HTTPException as error:
            assert error.status_code == 403
            assert (
                error.detail
                == "Missing permission: job:status"
            )

    asyncio.run(run_test())


def test_auditor_can_read_analytics():
    async def run_test():
        checker = require_permission(
            Permission.ANALYTICS_READ
        )

        user = FakeUser(
            UserRole.AUDITOR
        )

        result = await checker(
            current_user=user
        )

        assert result is user

    asyncio.run(run_test())


def test_admin_can_manage_users():
    async def run_test():
        checker = require_permission(
            Permission.USER_MANAGE
        )

        user = FakeUser(
            UserRole.ADMIN
        )

        result = await checker(
            current_user=user
        )

        assert result is user

    asyncio.run(run_test())


def test_technician_cannot_manage_users():
    async def run_test():
        checker = require_permission(
            Permission.USER_MANAGE
        )

        user = FakeUser(
            UserRole.TECHNICIAN
        )

        try:
            await checker(
                current_user=user
            )
            assert False
        except HTTPException as error:
            assert error.status_code == 403
            assert (
                error.detail
                == "Missing permission: user:manage"
            )

    asyncio.run(run_test())


def test_auditor_cannot_manage_users():
    async def run_test():
        checker = require_permission(
            Permission.USER_MANAGE
        )

        user = FakeUser(
            UserRole.AUDITOR
        )

        try:
            await checker(
                current_user=user
            )
            assert False
        except HTTPException as error:
            assert error.status_code == 403
            assert (
                error.detail
                == "Missing permission: user:manage"
            )

    asyncio.run(run_test())


def test_all_roles_have_permission_sets():
    assert set(ROLE_PERMISSIONS.keys()) == {
        UserRole.ADMIN,
        UserRole.TECHNICIAN,
        UserRole.AUDITOR,
    }


def test_permission_names_are_unique():
    values = [
        permission.value
        for permission in Permission
    ]

    assert len(values) == len(set(values))
