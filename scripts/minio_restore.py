"""Restore a MinIO backup into an explicitly confirmed empty bucket or prefix."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from scripts.backup_contract import BackupContractError
from scripts.minio_backup import client_from_environment, restore_minio_backup


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--target-bucket", required=True)
    parser.add_argument("--confirm-target", required=True)
    parser.add_argument("--allow-bucket")
    parser.add_argument("--target-prefix", default="")
    args = parser.parse_args()
    allowed = args.allow_bucket or os.getenv("BACKUP_MINIO_RESTORE_ALLOWED_BUCKET")
    if not allowed:
        parser.error("--allow-bucket or BACKUP_MINIO_RESTORE_ALLOWED_BUCKET is required")
    try:
        restore_minio_backup(
            args.manifest,
            client_from_environment(),
            args.target_bucket,
            confirmed_bucket=args.confirm_target,
            allowed_bucket=allowed,
            target_prefix=args.target_prefix,
        )
    except BackupContractError as exc:
        parser.error(str(exc))
    print(f"restored_bucket={args.target_bucket}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
