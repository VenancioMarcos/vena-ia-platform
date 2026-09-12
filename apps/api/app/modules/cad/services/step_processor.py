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
            )
            self._gateway.mark_completed(job_id, profile_data)
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
