import asyncio
from datetime import datetime, timedelta, timezone

from httpx import ASGITransport, AsyncClient
from sqlalchemy import update

from app.database import AsyncSessionLocal
from app.main import app
from app.models.refresh_token import RefreshToken
from app.security import hash_refresh_token


test_loop = asyncio.new_event_loop()


async def login(client):
    response = await client.post(
        "/auth/token",
        data={
            "username": "admin",
            "password": "AdminPass123!",
        },
    )

    assert response.status_code == 200
    return response.json()


def test_valid_refresh_token():
    async def run_test():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:

            tokens = await login(client)

            response = await client.post(
                "/auth/refresh",
                json={
                    "refresh_token": tokens["refresh_token"]
                },
            )

            assert response.status_code == 200
            assert "access_token" in response.json()
            assert "refresh_token" in response.json()
            assert (
                response.json()["refresh_token"]
                != tokens["refresh_token"]
            )

    test_loop.run_until_complete(run_test())


def test_expired_refresh_token():
    async def run_test():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:

            tokens = await login(client)

            token_hash = hash_refresh_token(
                tokens["refresh_token"]
            )

            async with AsyncSessionLocal() as db:
                await db.execute(
                    update(RefreshToken)
                    .where(
                        RefreshToken.token_hash == token_hash
                    )
                    .values(
                        expires_at=(
                            datetime.now(timezone.utc)
                            - timedelta(minutes=1)
                        )
                    )
                )

                await db.commit()

            response = await client.post(
                "/auth/refresh",
                json={
                    "refresh_token": tokens["refresh_token"]
                },
            )

            assert response.status_code == 401

    test_loop.run_until_complete(run_test())


def test_reused_refresh_token():
    async def run_test():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:

            tokens = await login(client)

            old_refresh = tokens["refresh_token"]

            first_refresh = await client.post(
                "/auth/refresh",
                json={
                    "refresh_token": old_refresh
                },
            )

            assert first_refresh.status_code == 200

            reused = await client.post(
                "/auth/refresh",
                json={
                    "refresh_token": old_refresh
                },
            )

            assert reused.status_code == 401

    test_loop.run_until_complete(run_test())


def test_logout_invalidates_refresh_token():
    async def run_test():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:

            tokens = await login(client)

            refresh_token = tokens["refresh_token"]

            logout = await client.post(
                "/auth/logout",
                json={
                    "refresh_token": refresh_token
                },
            )

            assert logout.status_code == 200

            response = await client.post(
                "/auth/refresh",
                json={
                    "refresh_token": refresh_token
                },
            )

            assert response.status_code == 401

    test_loop.run_until_complete(run_test())


def test_server_side_pagination_filtering_sorting():
    async def run_test():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:

            tokens = await login(client)

            headers = {
                "Authorization":
                    f"Bearer {tokens['access_token']}"
            }

            # ATM page 1
            response = await client.get(
                "/atms",
                params={
                    "page": 1,
                    "size": 2,
                },
                headers=headers,
            )

            assert response.status_code == 200

            data = response.json()

            assert "items" in data
            assert "total" in data
            assert len(data["items"]) <= 2

            total = data["total"]

            # Page boundary
            far_page = await client.get(
                "/atms",
                params={
                    "page": 9999,
                    "size": 2,
                },
                headers=headers,
            )

            assert far_page.status_code == 200
            assert far_page.json()["items"] == []
            assert far_page.json()["total"] == total

            # Ascending sort
            ascending = await client.get(
                "/atms",
                params={
                    "size": 100,
                    "sort_by": "id",
                    "sort_dir": "asc",
                },
                headers=headers,
            )

            assert ascending.status_code == 200

            ascending_ids = [
                item["id"]
                for item
                in ascending.json()["items"]
            ]

            assert ascending_ids == sorted(
                ascending_ids
            )

            # Descending sort
            descending = await client.get(
                "/atms",
                params={
                    "size": 100,
                    "sort_by": "id",
                    "sort_dir": "desc",
                },
                headers=headers,
            )

            assert descending.status_code == 200

            descending_ids = [
                item["id"]
                for item
                in descending.json()["items"]
            ]

            assert descending_ids == sorted(
                descending_ids,
                reverse=True,
            )

            # Status, branch and search filters
            if ascending.json()["items"]:
                sample = ascending.json()["items"][0]

                status_filtered = await client.get(
                    "/atms",
                    params={
                        "status":
                            sample["status"]
                    },
                    headers=headers,
                )

                assert status_filtered.status_code == 200

                assert all(
                    item["status"]
                    == sample["status"]
                    for item
                    in status_filtered.json()["items"]
                )

                branch_filtered = await client.get(
                    "/atms",
                    params={
                        "branch_id":
                            sample["branch_id"]
                    },
                    headers=headers,
                )

                assert branch_filtered.status_code == 200

                assert all(
                    item["branch_id"]
                    == sample["branch_id"]
                    for item
                    in branch_filtered.json()["items"]
                )

                searched = await client.get(
                    "/atms",
                    params={
                        "search":
                            sample["serial_number"]
                    },
                    headers=headers,
                )

                assert searched.status_code == 200
                assert searched.json()["total"] >= 1

            # Invalid sort field
            invalid_sort = await client.get(
                "/atms",
                params={
                    "sort_by":
                        "DROP TABLE atms"
                },
                headers=headers,
            )

            assert invalid_sort.status_code == 422

            # Maximum page size
            oversized = await client.get(
                "/atms",
                params={
                    "size": 101
                },
                headers=headers,
            )

            assert oversized.status_code == 422

            # Service call page
            service_response = await client.get(
                "/service-call",
                params={
                    "page": 1,
                    "size": 2,
                },
                headers=headers,
            )

            assert service_response.status_code == 200

            service_data = service_response.json()

            assert "items" in service_data
            assert "total" in service_data
            assert len(service_data["items"]) <= 2

            # Service-call ascending / descending
            service_asc = await client.get(
                "/service-call",
                params={
                    "size": 100,
                    "sort_by": "id",
                    "sort_dir": "asc",
                },
                headers=headers,
            )

            service_desc = await client.get(
                "/service-call",
                params={
                    "size": 100,
                    "sort_by": "id",
                    "sort_dir": "desc",
                },
                headers=headers,
            )

            assert service_asc.status_code == 200
            assert service_desc.status_code == 200

            service_asc_ids = [
                item["id"]
                for item
                in service_asc.json()["items"]
            ]

            service_desc_ids = [
                item["id"]
                for item
                in service_desc.json()["items"]
            ]

            assert service_asc_ids == sorted(
                service_asc_ids
            )

            assert service_desc_ids == sorted(
                service_desc_ids,
                reverse=True,
            )

            if service_asc.json()["items"]:
                service_sample = (
                    service_asc.json()["items"][0]
                )

                service_status = await client.get(
                    "/service-call",
                    params={
                        "status":
                            service_sample["status"]
                    },
                    headers=headers,
                )

                assert service_status.status_code == 200

                assert all(
                    item["status"]
                    == service_sample["status"]
                    for item
                    in service_status.json()["items"]
                )

            service_invalid_sort = await client.get(
                "/service-call",
                params={
                    "sort_by":
                        "not_a_column"
                },
                headers=headers,
            )

            assert (
                service_invalid_sort.status_code
                == 422
            )

            # Auth still applies when filters are present
            unauthenticated = await client.get(
                "/atms",
                params={
                    "branch_id": 1,
                    "sort_by": "id",
                },
            )

            assert unauthenticated.status_code == 401

    test_loop.run_until_complete(run_test())
