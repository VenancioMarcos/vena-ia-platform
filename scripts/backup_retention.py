"""Safe retention planning and atomic removal for complete encrypted backup sets."""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from scripts.backup_contract import BackupContractError, ensure_outside_repository
from scripts.encrypted_backup import EncryptionKey, EncryptedSetManifest, load_encrypted_manifest


@dataclass(frozen=True)
class RetentionPolicy:
    daily_keep: int = 7
    weekly_keep: int = 5
    monthly_keep: int = 12
    daily_max_age_days: int = 14
    weekly_max_age_days: int = 60
    monthly_max_age_days: int = 400

    def validate(self) -> None:
        values = asdict(self).values()
        if any(not isinstance(value, int) or value < 1 for value in values):
            raise BackupContractError("Retention policy values must be positive integers")

    def keep_for(self, retention_class: str) -> int:
        return {
            "daily": self.daily_keep,
            "weekly": self.weekly_keep,
            "monthly": self.monthly_keep,
        }[retention_class]

    def max_age_for(self, retention_class: str) -> int:
        return {
            "daily": self.daily_max_age_days,
            "weekly": self.weekly_max_age_days,
            "monthly": self.monthly_max_age_days,
        }[retention_class]


@dataclass(frozen=True)
class RetentionDecision:
    backup_set: str
    action: str
    reason: str


@dataclass(frozen=True)
class RetentionReport:
    dry_run: bool
    maintained: int
    removed: int
    decisions: list[RetentionDecision]


def _created_at(manifest: EncryptedSetManifest) -> datetime:
    value = datetime.fromisoformat(manifest.created_at.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise BackupContractError("Backup retention timestamp must include a timezone")
    return value.astimezone(timezone.utc)


def execute_retention(
    authorized_root: Path,
    key: EncryptionKey,
    policy: RetentionPolicy,
    *,
    now: datetime | None = None,
    apply: bool = False,
    confirmed_root: Path | None = None,
) -> RetentionReport:
    policy.validate()
    root = ensure_outside_repository(authorized_root)
    if not root.is_dir() or root.is_symlink():
        raise BackupContractError("Retention root is missing or unsafe")
    if apply and (
        confirmed_root is None or ensure_outside_repository(confirmed_root).resolve() != root.resolve()
    ):
        raise BackupContractError("Retention root was not explicitly confirmed")
    if any(root.glob(".vena-ia-encrypted-*.deleting")):
        raise BackupContractError("Retention found an unfinished prior deletion")
    sets: list[tuple[Path, EncryptedSetManifest]] = []
    for candidate in sorted(root.glob("vena-ia-encrypted-*")):
        if not candidate.is_dir() or candidate.is_symlink() or candidate.parent.resolve() != root:
            raise BackupContractError("Retention encountered an incomplete or unsafe backup set")
        manifest = load_encrypted_manifest(candidate / "encrypted-set.json", key)
        sets.append((candidate, manifest))
    if not sets:
        raise BackupContractError("Retention found no complete backup sets")

    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    decisions: dict[Path, RetentionDecision] = {}
    for retention_class in ("daily", "weekly", "monthly"):
        members = sorted(
            (item for item in sets if item[1].retention_class == retention_class),
            key=lambda item: _created_at(item[1]),
            reverse=True,
        )
        for position, (path, manifest) in enumerate(members):
            age_days = max(0, (current - _created_at(manifest)).days)
            if manifest.protected:
                decision = RetentionDecision(path.name, "maintain", "protected")
            elif position >= policy.keep_for(retention_class):
                decision = RetentionDecision(path.name, "remove", "quantity")
            elif age_days > policy.max_age_for(retention_class):
                decision = RetentionDecision(path.name, "remove", "age")
            else:
                decision = RetentionDecision(path.name, "maintain", "policy")
            decisions[path] = decision

    removable = [path for path, decision in decisions.items() if decision.action == "remove"]
    if len(removable) == len(sets):
        newest = max(sets, key=lambda item: _created_at(item[1]))[0]
        decisions[newest] = RetentionDecision(newest.name, "maintain", "last-valid-set")
        removable.remove(newest)

    if apply:
        staged: list[tuple[Path, Path]] = []
        try:
            for path in removable:
                trash = root / f".{path.name}.deleting"
                if trash.exists() or trash.is_symlink():
                    raise BackupContractError("Retention cleanup target already exists")
                path.replace(trash)
                staged.append((path, trash))
        except (OSError, BackupContractError) as exc:
            for original, trash in reversed(staged):
                if trash.exists() and not original.exists():
                    trash.replace(original)
            if isinstance(exc, BackupContractError):
                raise
            raise BackupContractError("Retention could not stage complete sets atomically") from exc
        try:
            for _, trash in staged:
                shutil.rmtree(trash)
        except OSError as exc:
            raise BackupContractError(
                "Retention cleanup was interrupted; manual recovery is required"
            ) from exc

    ordered = [decisions[path] for path, _ in sorted(sets, key=lambda item: item[0].name)]
    removed = len(removable)
    return RetentionReport(
        dry_run=not apply,
        maintained=len(sets) - removed,
        removed=removed,
        decisions=ordered,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--confirm-root", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--daily-keep", type=int, default=7)
    parser.add_argument("--weekly-keep", type=int, default=5)
    parser.add_argument("--monthly-keep", type=int, default=12)
    parser.add_argument("--daily-max-age-days", type=int, default=14)
    parser.add_argument("--weekly-max-age-days", type=int, default=60)
    parser.add_argument("--monthly-max-age-days", type=int, default=400)
    args = parser.parse_args()
    policy = RetentionPolicy(
        daily_keep=args.daily_keep,
        weekly_keep=args.weekly_keep,
        monthly_keep=args.monthly_keep,
        daily_max_age_days=args.daily_max_age_days,
        weekly_max_age_days=args.weekly_max_age_days,
        monthly_max_age_days=args.monthly_max_age_days,
    )
    try:
        report = execute_retention(
            args.root,
            EncryptionKey.from_environment(),
            policy,
            apply=args.apply,
            confirmed_root=args.confirm_root,
        )
    except BackupContractError as exc:
        parser.error(str(exc))
    print(json.dumps(asdict(report), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
