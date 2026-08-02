"""Authenticated encrypted backup-set bundles with no plaintext persistence."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterator
from uuid import UUID, uuid4

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from scripts.backup_contract import (
    BackupContractError,
    BackupManifest,
    ensure_outside_repository,
    sha256_file,
)
from scripts.backup_set import BackupSetManifest
from scripts.minio_backup import MinioBackupManifest

ENCRYPTED_SET_CONTRACT_VERSION = "vena-ia.encrypted-backup-set/v1"
ENCRYPTION_ALGORITHM = "AES-256-GCM"
_CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class EncryptionKey:
    key_id: str
    value: bytes

    def __post_init__(self) -> None:
        if len(self.value) != 32:
            raise BackupContractError("Backup encryption key must contain exactly 32 bytes")
        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
        if not self.key_id or len(self.key_id) > 128 or any(
            character not in allowed for character in self.key_id
        ):
            raise BackupContractError("Backup encryption key ID is invalid")

    @classmethod
    def from_environment(cls) -> EncryptionKey:
        key_id = os.getenv("BACKUP_ENCRYPTION_KEY_ID", "")
        encoded = os.getenv("BACKUP_ENCRYPTION_KEY", "")
        if not key_id or not encoded:
            raise BackupContractError("Backup encryption key and key ID are required")
        try:
            value = base64.b64decode(encoded, validate=True)
        except ValueError as exc:
            raise BackupContractError("Backup encryption key format is invalid") from exc
        return cls(key_id, value)


@dataclass(frozen=True)
class EncryptedArtifact:
    logical_path: str
    encrypted_path: str
    plaintext_size: int
    plaintext_sha256: str
    ciphertext_size: int
    ciphertext_sha256: str
    nonce_b64: str
    tag_b64: str


@dataclass(frozen=True)
class EncryptedSetManifest:
    contract_version: str
    backup_set_id: str
    created_at: str
    application_version: str
    migration_head: str
    encryption_algorithm: str
    key_id: str
    retention_class: str
    protected: bool
    artifacts: list[EncryptedArtifact]


@dataclass(frozen=True)
class EncryptedSetIndex:
    contract_version: str
    encryption_algorithm: str
    key_id: str
    manifest_file: str
    nonce_b64: str
    tag_b64: str
    ciphertext_sha256: str

    @classmethod
    def load(cls, path: Path) -> EncryptedSetIndex:
        try:
            payload: Any = json.loads(path.read_text(encoding="utf-8"))
            index = cls(**payload)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
            raise BackupContractError("Encrypted backup index is invalid") from exc
        if (
            index.contract_version != ENCRYPTED_SET_CONTRACT_VERSION
            or index.encryption_algorithm != ENCRYPTION_ALGORITHM
        ):
            raise BackupContractError("Encrypted backup algorithm or contract is unsupported")
        if PurePosixPath(index.manifest_file).name != index.manifest_file:
            raise BackupContractError("Encrypted manifest path is unsafe")
        if not _is_sha256(index.ciphertext_sha256):
            raise BackupContractError("Encrypted manifest checksum is invalid")
        _decode_nonce(index.nonce_b64)
        _decode_tag(index.tag_b64)
        return index


@dataclass(frozen=True)
class DecryptedSetPaths:
    root: Path
    postgres_manifest: Path
    minio_manifest: Path
    backup_set_manifest: Path


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _decode_nonce(value: str) -> bytes:
    try:
        nonce = base64.b64decode(value, validate=True)
    except ValueError as exc:
        raise BackupContractError("Encrypted backup nonce is invalid") from exc
    if len(nonce) != 12:
        raise BackupContractError("Encrypted backup nonce has an invalid size")
    return nonce


def _decode_tag(value: str) -> bytes:
    try:
        tag = base64.b64decode(value, validate=True)
    except ValueError as exc:
        raise BackupContractError("Encrypted backup tag is invalid") from exc
    if len(tag) != 16:
        raise BackupContractError("Encrypted backup tag has an invalid size")
    return tag


def _safe_relative(value: str) -> tuple[str, ...]:
    path = PurePosixPath(value)
    if (
        not value
        or "\\" in value
        or "\x00" in value
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise BackupContractError("Encrypted backup path is unsafe")
    return path.parts


def _safe_child(root: Path, relative: str) -> Path:
    target = root.joinpath(*_safe_relative(relative))
    current = target
    while current != root.parent:
        if current.exists() and current.is_symlink():
            raise BackupContractError("Symlinks are forbidden in encrypted backup sets")
        if current == root:
            break
        current = current.parent
    if root.resolve() not in target.resolve().parents:
        raise BackupContractError("Encrypted backup path escapes its root")
    return target


def _aad(backup_set_id: str, key_id: str, logical_path: str) -> bytes:
    return f"{ENCRYPTED_SET_CONTRACT_VERSION}\0{backup_set_id}\0{key_id}\0{logical_path}".encode()


def _encrypt_file(
    source: Path,
    target: Path,
    key: EncryptionKey,
    backup_set_id: str,
    logical_path: str,
) -> EncryptedArtifact:
    if not source.is_file() or source.is_symlink():
        raise BackupContractError("Plaintext backup artifact is missing or unsafe")
    nonce = os.urandom(12)
    encryptor = Cipher(algorithms.AES(key.value), modes.GCM(nonce)).encryptor()
    encryptor.authenticate_additional_data(_aad(backup_set_id, key.key_id, logical_path))
    plaintext_digest = hashlib.sha256()
    ciphertext_digest = hashlib.sha256()
    plaintext_size = 0
    ciphertext_size = 0
    target.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as input_file, target.open("xb") as output_file:
        for block in iter(lambda: input_file.read(_CHUNK_SIZE), b""):
            plaintext_digest.update(block)
            plaintext_size += len(block)
            encrypted = encryptor.update(block)
            output_file.write(encrypted)
            ciphertext_digest.update(encrypted)
            ciphertext_size += len(encrypted)
        final = encryptor.finalize()
        output_file.write(final)
        ciphertext_digest.update(final)
        ciphertext_size += len(final)
    return EncryptedArtifact(
        logical_path=logical_path,
        encrypted_path=target.name,
        plaintext_size=plaintext_size,
        plaintext_sha256=plaintext_digest.hexdigest(),
        ciphertext_size=ciphertext_size,
        ciphertext_sha256=ciphertext_digest.hexdigest(),
        nonce_b64=base64.b64encode(nonce).decode("ascii"),
        tag_b64=base64.b64encode(encryptor.tag).decode("ascii"),
    )


def _validate_source_manifests(
    postgres_path: Path,
    minio_path: Path,
    backup_set_path: Path,
) -> tuple[BackupManifest, MinioBackupManifest, BackupSetManifest]:
    postgres_path = ensure_outside_repository(postgres_path)
    minio_path = ensure_outside_repository(minio_path)
    backup_set_path = ensure_outside_repository(backup_set_path)
    postgres = BackupManifest.load(postgres_path)
    minio = MinioBackupManifest.load(minio_path)
    combined = BackupSetManifest.load(backup_set_path)
    if not (
        postgres.backup_set_id == minio.backup_set_id == combined.backup_set_id
        and postgres.created_at == minio.created_at == combined.created_at
        and postgres.application_version
        == minio.application_version
        == combined.application_version
    ):
        raise BackupContractError("Backup set source manifests disagree")
    if combined.migration_head != postgres.migration_head:
        raise BackupContractError("Backup set migration head disagrees")
    if (
        combined.postgres_manifest_sha256 != sha256_file(postgres_path)
        or combined.minio_manifest_sha256 != sha256_file(minio_path)
    ):
        raise BackupContractError("Backup set source manifest checksum disagrees")
    return postgres, minio, combined


def _source_files(
    postgres_path: Path,
    minio_path: Path,
    backup_set_path: Path,
    postgres: BackupManifest,
    minio: MinioBackupManifest,
) -> Iterator[tuple[str, Path]]:
    yield f"postgres/{postgres_path.name}", postgres_path
    yield f"postgres/{postgres.backup_file}", postgres_path.parent / postgres.backup_file
    yield f"minio/{minio_path.name}", minio_path
    for entry in minio.objects:
        yield f"minio/{entry.artifact_path}", minio_path.parent / entry.artifact_path
    yield f"backup-set/{backup_set_path.name}", backup_set_path


def create_encrypted_bundle(
    output_directory: Path,
    postgres_manifest_path: Path,
    minio_manifest_path: Path,
    backup_set_manifest_path: Path,
    key: EncryptionKey,
    *,
    retention_class: str = "daily",
    protected: bool = False,
) -> tuple[Path, Path]:
    if retention_class not in {"daily", "weekly", "monthly"}:
        raise BackupContractError("Backup retention class is unsupported")
    output = ensure_outside_repository(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    postgres, minio, combined = _validate_source_manifests(
        postgres_manifest_path, minio_manifest_path, backup_set_manifest_path
    )
    try:
        UUID(combined.backup_set_id)
    except ValueError as exc:
        raise BackupContractError("Backup set identifier is invalid") from exc
    root = output / f"vena-ia-encrypted-{combined.backup_set_id}"
    if root.exists():
        raise BackupContractError("Encrypted backup set exists; refusing overwrite")
    root.mkdir()
    artifacts: list[EncryptedArtifact] = []
    try:
        for artifact_index, (logical_path, source) in enumerate(
            _source_files(
                postgres_manifest_path,
                minio_manifest_path,
                backup_set_manifest_path,
                postgres,
                minio,
            )
        ):
            _safe_relative(logical_path)
            target = root / "artifacts" / f"{artifact_index:06d}.enc"
            artifacts.append(
                _encrypt_file(source, target, key, combined.backup_set_id, logical_path)
            )
        inner = EncryptedSetManifest(
            contract_version=ENCRYPTED_SET_CONTRACT_VERSION,
            backup_set_id=combined.backup_set_id,
            created_at=combined.created_at,
            application_version=combined.application_version,
            migration_head=combined.migration_head,
            encryption_algorithm=ENCRYPTION_ALGORITHM,
            key_id=key.key_id,
            retention_class=retention_class,
            protected=protected,
            artifacts=artifacts,
        )
        inner_bytes = (json.dumps(asdict(inner), sort_keys=True, separators=(",", ":")) + "\n").encode()
        manifest_nonce = os.urandom(12)
        manifest_aad = _aad(combined.backup_set_id, key.key_id, "manifest")
        manifest_cipher = Cipher(algorithms.AES(key.value), modes.GCM(manifest_nonce)).encryptor()
        manifest_cipher.authenticate_additional_data(manifest_aad)
        encrypted_manifest = manifest_cipher.update(inner_bytes) + manifest_cipher.finalize()
        manifest_file = root / "manifest.enc"
        manifest_file.write_bytes(encrypted_manifest)
        index = EncryptedSetIndex(
            contract_version=ENCRYPTED_SET_CONTRACT_VERSION,
            encryption_algorithm=ENCRYPTION_ALGORITHM,
            key_id=key.key_id,
            manifest_file=manifest_file.name,
            nonce_b64=base64.b64encode(manifest_nonce).decode("ascii"),
            tag_b64=base64.b64encode(manifest_cipher.tag).decode("ascii"),
            ciphertext_sha256=hashlib.sha256(encrypted_manifest).hexdigest(),
        )
        index_path = root / "encrypted-set.json"
        index_path.write_text(
            json.dumps(asdict(index), indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except (OSError, BackupContractError, InvalidTag, ValueError):
        shutil.rmtree(root, ignore_errors=True)
        raise
    return root, index_path


def load_encrypted_manifest(index_path: Path, key: EncryptionKey) -> EncryptedSetManifest:
    safe_index = ensure_outside_repository(index_path)
    index = EncryptedSetIndex.load(safe_index)
    if index.key_id != key.key_id:
        raise BackupContractError("Encrypted backup key ID does not match")
    manifest_path = _safe_child(safe_index.parent, index.manifest_file)
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise BackupContractError("Encrypted backup manifest is missing or unsafe")
    ciphertext = manifest_path.read_bytes()
    if hashlib.sha256(ciphertext).hexdigest() != index.ciphertext_sha256:
        raise BackupContractError("Encrypted backup manifest was tampered")
    decryptor = Cipher(
        algorithms.AES(key.value),
        modes.GCM(_decode_nonce(index.nonce_b64), _decode_tag(index.tag_b64)),
    ).decryptor()
    # The set ID is authenticated inside the encrypted payload; try candidate roots only after decrypt.
    try:
        # Manifest AAD needs the set UUID. It is encoded in the directory name by contract.
        set_id = safe_index.parent.name.removeprefix("vena-ia-encrypted-")
        UUID(set_id)
        decryptor.authenticate_additional_data(_aad(set_id, key.key_id, "manifest"))
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        payload: Any = json.loads(plaintext)
        artifacts = [EncryptedArtifact(**item) for item in payload.pop("artifacts")]
        manifest = EncryptedSetManifest(artifacts=artifacts, **payload)
    except (InvalidTag, ValueError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise BackupContractError("Encrypted backup authentication failed") from exc
    if (
        manifest.contract_version != ENCRYPTED_SET_CONTRACT_VERSION
        or manifest.encryption_algorithm != ENCRYPTION_ALGORITHM
        or manifest.backup_set_id != set_id
        or manifest.key_id != key.key_id
        or manifest.retention_class not in {"daily", "weekly", "monthly"}
    ):
        raise BackupContractError("Encrypted backup manifest metadata is invalid")
    try:
        datetime.fromisoformat(manifest.created_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise BackupContractError("Encrypted backup creation time is invalid") from exc
    logical_paths: set[str] = set()
    encrypted_paths: set[str] = set()
    for artifact in manifest.artifacts:
        _safe_relative(artifact.logical_path)
        _safe_relative(artifact.encrypted_path)
        if artifact.logical_path in logical_paths or artifact.encrypted_path in encrypted_paths:
            raise BackupContractError("Encrypted backup artifact is duplicated")
        logical_paths.add(artifact.logical_path)
        encrypted_paths.add(artifact.encrypted_path)
        if not _is_sha256(artifact.plaintext_sha256) or not _is_sha256(
            artifact.ciphertext_sha256
        ):
            raise BackupContractError("Encrypted backup artifact checksum is invalid")
        _decode_nonce(artifact.nonce_b64)
        _decode_tag(artifact.tag_b64)
        encrypted = _safe_child(safe_index.parent / "artifacts", artifact.encrypted_path)
        if (
            not encrypted.is_file()
            or encrypted.is_symlink()
            or encrypted.stat().st_size != artifact.ciphertext_size
            or sha256_file(encrypted) != artifact.ciphertext_sha256
        ):
            raise BackupContractError("Encrypted backup artifact is incomplete or corrupted")
    return manifest


def decrypt_bundle(index_path: Path, output_directory: Path, key: EncryptionKey) -> DecryptedSetPaths:
    safe_index = ensure_outside_repository(index_path)
    manifest = load_encrypted_manifest(safe_index, key)
    target = ensure_outside_repository(output_directory)
    if target.exists():
        raise BackupContractError("Decryption destination exists; refusing overwrite")
    partial = target.parent / f".{target.name}.partial-{uuid4().hex}"
    partial.mkdir(parents=True)
    try:
        partial.chmod(0o700)
    except OSError:
        pass
    try:
        for artifact in manifest.artifacts:
            source = _safe_child(safe_index.parent / "artifacts", artifact.encrypted_path)
            destination = _safe_child(partial, artifact.logical_path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            decryptor = Cipher(
                algorithms.AES(key.value),
                modes.GCM(_decode_nonce(artifact.nonce_b64), _decode_tag(artifact.tag_b64)),
            ).decryptor()
            decryptor.authenticate_additional_data(
                _aad(manifest.backup_set_id, key.key_id, artifact.logical_path)
            )
            digest = hashlib.sha256()
            size = 0
            with source.open("rb") as input_file, destination.open("xb") as output_file:
                for block in iter(lambda: input_file.read(_CHUNK_SIZE), b""):
                    plaintext = decryptor.update(block)
                    output_file.write(plaintext)
                    digest.update(plaintext)
                    size += len(plaintext)
                final = decryptor.finalize()
                output_file.write(final)
                digest.update(final)
                size += len(final)
            try:
                destination.chmod(0o600)
            except OSError:
                pass
            if size != artifact.plaintext_size or digest.hexdigest() != artifact.plaintext_sha256:
                raise BackupContractError("Decrypted backup artifact integrity failed")
        partial.replace(target)
    except (OSError, InvalidTag, BackupContractError) as exc:
        shutil.rmtree(partial, ignore_errors=True)
        if isinstance(exc, InvalidTag):
            raise BackupContractError("Encrypted backup authentication failed") from exc
        raise
    postgres_manifests = list((target / "postgres").glob("*.manifest.json"))
    minio_manifest = target / "minio" / "manifest.json"
    backup_set_manifests = list((target / "backup-set").glob("*.json"))
    if len(postgres_manifests) != 1 or len(backup_set_manifests) != 1:
        shutil.rmtree(target, ignore_errors=True)
        raise BackupContractError("Decrypted backup set structure is incomplete")
    return DecryptedSetPaths(target, postgres_manifests[0], minio_manifest, backup_set_manifests[0])
