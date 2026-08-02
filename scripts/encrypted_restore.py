"""Authenticate and decrypt one backup set into a new restricted restore directory."""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.backup_contract import BackupContractError
from scripts.encrypted_backup import EncryptionKey, decrypt_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args()
    try:
        paths = decrypt_bundle(
            args.index,
            args.output_directory,
            EncryptionKey.from_environment(),
        )
    except BackupContractError as exc:
        parser.error(str(exc))
    print(f"restore_root={paths.root}")
    print(f"postgres_manifest={paths.postgres_manifest}")
    print(f"minio_manifest={paths.minio_manifest}")
    print(f"backup_set_manifest={paths.backup_set_manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
