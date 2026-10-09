import asyncio
import boto3
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.diagnostic_report import DiagnosticReport

BUCKET_NAME = "cashcow-diagnostic-reports-2478"
PREFIX = "diagnostic-reports/"


def extract_s3_key(file_url: str) -> str:
    without_scheme = file_url.removeprefix("s3://")
    _, _, key = without_scheme.partition("/")
    return key


def list_s3_keys() -> set[str]:
    s3_client = boto3.client("s3")
    paginator = s3_client.get_paginator("list_objects_v2")

    keys = set()

    for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix=PREFIX):
        for obj in page.get("Contents", []):
            keys.add(obj["Key"])

    return keys


async def main() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(DiagnosticReport))
        reports = result.scalars().all()

    db_keys = {
        extract_s3_key(report.file_url)
        for report in reports
        if report.file_url.startswith(f"s3://{BUCKET_NAME}/")
    }

    s3_keys = list_s3_keys()

    print("Healthy:", sorted(db_keys & s3_keys))
    print("Broken:", sorted(db_keys - s3_keys))
    print("Orphaned:", sorted(s3_keys - db_keys))


if __name__ == "__main__":
    asyncio.run(main())
