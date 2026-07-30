from pydantic import BaseModel


class BoundingBoxResponse(BaseModel):
    minimum: tuple[float, float, float]
    maximum: tuple[float, float, float]
    dimensions: tuple[float, float, float]


class CADAnalysisResponse(BaseModel):
    document_id: str
    source_filename: str
    step_filename: str | None
    schema_name: str | None
    entity_count: int
    entity_types: dict[str, int]
    cartesian_point_count: int
    bounding_box: BoundingBoxResponse | None
    length_unit: str
    volume: float | None
    volume_status: str
    report: str
