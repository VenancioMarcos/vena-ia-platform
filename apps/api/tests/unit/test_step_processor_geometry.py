import pytest

from app.modules.cad.ingestion_schemas import CadProfilePoint
from app.modules.cad.services.step_processor import (
    InvalidProfileGeometryError,
    StepProcessingPolicy,
    validate_profile_geometry,
)


def _point(r_mm: float, z_mm: float) -> CadProfilePoint:
    return CadProfilePoint(r_mm=r_mm, z_mm=z_mm)


def test_accepts_axis_closed_profile_without_warning() -> None:
    points = (_point(0, 0), _point(25, 0), _point(25, -100), _point(0, -100))
    assert validate_profile_geometry(points, policy=StepProcessingPolicy()) == ()


def test_reports_small_closure_gap_for_mandatory_review() -> None:
    points = (_point(1, 0), _point(10, -5), _point(1.02, 0.01))
    assert validate_profile_geometry(points, policy=StepProcessingPolicy()) == (
        "PROFILE_CLOSURE_GAP_WITHIN_TOLERANCE",
    )


@pytest.mark.parametrize(
    ("points", "reason"),
    [
        (
            (_point(0, 0), _point(2, 0), _point(2, 0), _point(0, -2)),
            "PROFILE_DEGENERATE_SEGMENT",
        ),
        (
            (_point(1, 0), _point(2, 0), _point(2, -2), _point(1, -2)),
            "PROFILE_OPEN_OR_DISCONTINUOUS",
        ),
        (
            (
                _point(0, 0),
                _point(2, -2),
                _point(0, -2),
                _point(2, 0),
                _point(0, 0),
            ),
            "PROFILE_SELF_INTERSECTION",
        ),
        (
            (_point(0, 0), _point(5_001, 0), _point(5_001, -1), _point(0, -1)),
            "PROFILE_DIMENSION_LIMIT_EXCEEDED",
        ),
    ],
)
def test_rejects_invalid_profiles(
    points: tuple[CadProfilePoint, ...],
    reason: str,
) -> None:
    with pytest.raises(InvalidProfileGeometryError, match=f"^{reason}$"):
        validate_profile_geometry(points, policy=StepProcessingPolicy())
