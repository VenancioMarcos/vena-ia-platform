"""Conservative ISO 10303-21 (STEP Part 21) metadata parser."""

import re
from dataclasses import dataclass


class StepParseError(Exception):
    pass


@dataclass(frozen=True)
class BoundingBox:
    minimum: tuple[float, float, float]
    maximum: tuple[float, float, float]

    @property
    def dimensions(self) -> tuple[float, float, float]:
        return tuple(
            maximum - minimum
            for minimum, maximum in zip(self.minimum, self.maximum, strict=True)
        )  # type: ignore[return-value]


@dataclass(frozen=True)
class StepAnalysis:
    filename: str | None
    schema: str | None
    entity_count: int
    entity_types: dict[str, int]
    cartesian_point_count: int
    bounding_box: BoundingBox | None
    length_unit: str
    volume: float | None
    volume_status: str


class StepTextParser:
    """Extracts auditable metadata without executing or resolving STEP entities."""

    _entity = re.compile(r"#[0-9]+\s*=\s*([A-Z0-9_]+)\s*\(", re.IGNORECASE)
    _point = re.compile(
        r"CARTESIAN_POINT\s*\([^,]*,\s*\(\s*"
        r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[ED][-+]?\d+)?)\s*,\s*"
        r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[ED][-+]?\d+)?)\s*,\s*"
        r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[ED][-+]?\d+)?)\s*\)\s*\)",
        re.IGNORECASE,
    )
    _file_name = re.compile(r"FILE_NAME\s*\(\s*'([^']*)'", re.IGNORECASE)
    _schema = re.compile(r"FILE_SCHEMA\s*\(\s*\(\s*'([^']+)'", re.IGNORECASE)

    def parse(self, content: bytes) -> StepAnalysis:
        if not content.startswith(b"ISO-10303-21;"):
            raise StepParseError("Invalid STEP Part 21 signature")
        if b"\x00" in content:
            raise StepParseError("STEP file contains invalid binary content")
        text = content.decode("latin-1")
        if "END-ISO-10303-21;" not in text.upper():
            raise StepParseError("STEP Part 21 terminator is missing")

        entity_types: dict[str, int] = {}
        for raw_type in self._entity.findall(text):
            entity_type = raw_type.upper()
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

        points: list[tuple[float, float, float]] = []
        for coordinates in self._point.findall(text):
            try:
                x, y, z = (
                    float(value.replace("D", "E")) for value in coordinates
                )
                points.append((x, y, z))
            except ValueError as exc:
                raise StepParseError("STEP contains invalid Cartesian coordinates") from exc

        bounding_box = self._bounding_box(points)
        filename_match = self._file_name.search(text)
        schema_match = self._schema.search(text)
        return StepAnalysis(
            filename=filename_match.group(1) if filename_match else None,
            schema=schema_match.group(1) if schema_match else None,
            entity_count=sum(entity_types.values()),
            entity_types=dict(sorted(entity_types.items())),
            cartesian_point_count=len(points),
            bounding_box=bounding_box,
            length_unit=self._length_unit(text),
            volume=None,
            volume_status="UNAVAILABLE_WITHOUT_GEOMETRY_KERNEL",
        )

    @staticmethod
    def _bounding_box(
        points: list[tuple[float, float, float]],
    ) -> BoundingBox | None:
        if not points:
            return None
        axes = tuple(zip(*points, strict=True))
        return BoundingBox(
            minimum=tuple(min(axis) for axis in axes),  # type: ignore[arg-type]
            maximum=tuple(max(axis) for axis in axes),  # type: ignore[arg-type]
        )

    @staticmethod
    def _length_unit(text: str) -> str:
        normalized = text.upper()
        if "SI_UNIT(.MILLI.,.METRE.)" in normalized:
            return "mm"
        if "SI_UNIT($,.METRE.)" in normalized:
            return "m"
        if "CONVERSION_BASED_UNIT('INCH'" in normalized:
            return "in"
        return "UNKNOWN"
