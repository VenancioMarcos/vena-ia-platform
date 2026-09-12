import math
from dataclasses import dataclass

from app.modules.cad.ingestion import CadIngestionGateway
from app.modules.cad.ingestion_schemas import (
    CadProfileBoundingBox,
    CadProfileData,
    CadProfilePoint,
)
from app.modules.cad.kernel import OpenCascadeGeometryKernel
from app.modules.cad.parser import StepTextParser
from app.modules.cad.profile_extractor import TurningDatum, extract_turning_profile


@dataclass(frozen=True)
class StepProcessingPolicy:
    """Declared RZ convention for this bounded route; never machine authority."""

    datum: TurningDatum = TurningDatum(
        origin_mm=(0.0, 0.0, 0.0),
        axis_direction=(0.0, 0.0, 1.0),
    )
    linear_tolerance_mm: float = 1e-6
    angular_tolerance_rad: float = 1e-7
    closure_tolerance_mm: float = 0.05
    max_radius_mm: float = 5_000.0
    max_z_span_mm: float = 10_000.0


class InvalidProfileGeometryError(ValueError):
    """Sanitized, stable failure reason safe for the public job status."""


def _orientation(
    a: CadProfilePoint,
    b: CadProfilePoint,
    c: CadProfilePoint,
) -> float:
    return (b.z_mm - a.z_mm) * (c.r_mm - a.r_mm) - (b.r_mm - a.r_mm) * (
        c.z_mm - a.z_mm
    )


def _segments_intersect(
    first: tuple[CadProfilePoint, CadProfilePoint],
    second: tuple[CadProfilePoint, CadProfilePoint],
    *,
    tolerance_mm: float,
) -> bool:
    a, b = first
    c, d = second
    o1, o2 = _orientation(a, b, c), _orientation(a, b, d)
    o3, o4 = _orientation(c, d, a), _orientation(c, d, b)
    crosses = (
        ((o1 > tolerance_mm and o2 < -tolerance_mm) or (o1 < -tolerance_mm and o2 > tolerance_mm))
        and ((o3 > tolerance_mm and o4 < -tolerance_mm) or (o3 < -tolerance_mm and o4 > tolerance_mm))
    )
    if crosses:
        return True

    def on_segment(
        start: CadProfilePoint,
        end: CadProfilePoint,
        candidate: CadProfilePoint,
        orientation: float,
    ) -> bool:
        return (
            abs(orientation) <= tolerance_mm
            and min(start.z_mm, end.z_mm) - tolerance_mm
            <= candidate.z_mm
            <= max(start.z_mm, end.z_mm) + tolerance_mm
            and min(start.r_mm, end.r_mm) - tolerance_mm
            <= candidate.r_mm
            <= max(start.r_mm, end.r_mm) + tolerance_mm
        )

    return (
        on_segment(a, b, c, o1)
        or on_segment(a, b, d, o2)
        or on_segment(c, d, a, o3)
        or on_segment(c, d, b, o4)
    )


def validate_profile_geometry(
    points: tuple[CadProfilePoint, ...],
    *,
    policy: StepProcessingPolicy,
) -> tuple[str, ...]:
    """Validate a bounded RZ outline and return review-only quality warnings."""
    if len(points) < 3:
        raise InvalidProfileGeometryError("PROFILE_INSUFFICIENT_POINTS")
    if not math.isfinite(policy.closure_tolerance_mm) or (
        policy.closure_tolerance_mm <= policy.linear_tolerance_mm
    ):
        raise InvalidProfileGeometryError("PROFILE_TOLERANCE_INVALID")
    if any(
        not math.isfinite(point.r_mm)
        or not math.isfinite(point.z_mm)
        or point.r_mm < 0
        for point in points
    ):
        raise InvalidProfileGeometryError("PROFILE_POINT_INVALID")

    for start, end in zip(points, points[1:]):
        if math.hypot(end.r_mm - start.r_mm, end.z_mm - start.z_mm) <= policy.linear_tolerance_mm:
            raise InvalidProfileGeometryError("PROFILE_DEGENERATE_SEGMENT")

    max_radius = max(point.r_mm for point in points)
    z_span = max(point.z_mm for point in points) - min(point.z_mm for point in points)
    if max_radius > policy.max_radius_mm or z_span > policy.max_z_span_mm:
        raise InvalidProfileGeometryError("PROFILE_DIMENSION_LIMIT_EXCEEDED")

    warnings: list[str] = []
    first, last = points[0], points[-1]
    closure_gap = math.hypot(last.r_mm - first.r_mm, last.z_mm - first.z_mm)
    closes_on_axis = (
        first.r_mm <= policy.linear_tolerance_mm
        and last.r_mm <= policy.linear_tolerance_mm
    )
    if closure_gap > policy.linear_tolerance_mm and not closes_on_axis:
        if closure_gap <= policy.closure_tolerance_mm:
            warnings.append("PROFILE_CLOSURE_GAP_WITHIN_TOLERANCE")
        else:
            raise InvalidProfileGeometryError("PROFILE_OPEN_OR_DISCONTINUOUS")

    segments = list(zip(points, points[1:]))
    if closure_gap > policy.linear_tolerance_mm:
        segments.append((last, first))
    segment_count = len(segments)
    for first_index, first_segment in enumerate(segments):
        for second_index in range(first_index + 1, segment_count):
            adjacent = second_index == first_index + 1 or (
                first_index == 0 and second_index == segment_count - 1
            )
            if adjacent:
                continue
            if _segments_intersect(
                first_segment,
                segments[second_index],
                tolerance_mm=policy.linear_tolerance_mm,
            ):
                raise InvalidProfileGeometryError("PROFILE_SELF_INTERSECTION")
    return tuple(warnings)


class StepBackgroundProcessor:
    def __init__(
        self,
        gateway: CadIngestionGateway,
        *,
        kernel: OpenCascadeGeometryKernel | None = None,
        parser: StepTextParser | None = None,
        policy: StepProcessingPolicy | None = None,
    ) -> None:
        self._gateway = gateway
        self._kernel = kernel or OpenCascadeGeometryKernel()
        self._parser = parser or StepTextParser()
        self._policy = policy or StepProcessingPolicy()

    def process(self, job_id: str) -> None:
        """Process one validated sandbox file and retain only bounded status data."""
        try:
            self._gateway.mark_processing(job_id)
            job = self._gateway.get_job_for_processing(job_id)
            content = job.path.read_bytes()
            metadata = self._parser.parse(content)
            shape, geometry = self._kernel._load_step_shape(content)
            if not geometry.topology_valid:
                raise ValueError("STEP_TOPOLOGY_INVALID")
            extraction = extract_turning_profile(
                shape,
                datum=self._policy.datum,
                source_unit=metadata.length_unit,
                linear_tolerance_mm=self._policy.linear_tolerance_mm,
                angular_tolerance_rad=self._policy.angular_tolerance_rad,
            )
            if extraction.profile is None:
                reason = extraction.reasons[0] if extraction.reasons else "PROFILE_UNAVAILABLE"
                raise ValueError(reason)

            points = tuple(
                CadProfilePoint(r_mm=point.radius_mm, z_mm=point.z_mm)
                for point in extraction.profile.points
            )
            warnings = validate_profile_geometry(points, policy=self._policy)
            z_values = [point.z_mm for point in extraction.profile.points]
            profile_data = CadProfileData(
                points=points,
                bounding_box=CadProfileBoundingBox(
                    max_radius_mm=max(point.radius_mm for point in extraction.profile.points),
                    min_z_mm=min(z_values),
                    max_z_mm=max(z_values),
                    total_z_length_mm=max(z_values) - min(z_values),
                ),
                review_status="PROFILE_AVAILABLE_REQUIRES_REVIEW",
                warnings=warnings,
            )
            self._gateway.mark_completed(job_id, profile_data)
        except InvalidProfileGeometryError as exc:
            try:
                self._gateway.mark_failed(job_id, str(exc))
            except Exception:
                pass
        except Exception:
            try:
                self._gateway.mark_failed(job_id, "STEP_PROFILE_EXTRACTION_FAILED")
            except Exception:
                pass
        finally:
            try:
                self._gateway.delete_job_file(job_id)
            except Exception:
                pass


def build_step_background_processor(
    gateway: CadIngestionGateway,
) -> StepBackgroundProcessor:
    return StepBackgroundProcessor(gateway)
