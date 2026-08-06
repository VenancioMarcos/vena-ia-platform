from pathlib import Path

from scripts.runtime_policy import is_pinned_image_reference, validate_repository


ROOT = Path(__file__).resolve().parents[2]


def test_runtime_policy_matches_repository() -> None:
    assert validate_repository(ROOT) == []


def test_image_policy_rejects_floating_or_digest_only_references() -> None:
    assert not is_pinned_image_reference("minio/minio:latest")
    assert not is_pinned_image_reference("redis:7.4.7-alpine")
    assert not is_pinned_image_reference("redis@sha256:" + "a" * 64)


def test_image_policy_accepts_versioned_immutable_reference() -> None:
    assert is_pinned_image_reference("redis:7.4.7-alpine@sha256:" + "a" * 64)
