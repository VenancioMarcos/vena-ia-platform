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


class GeometryValue(BaseModel):
    value: float | None
    unit: str
    status: str


class GeometryAnalysisContract(BaseModel):
    schema_version: str = "vena-ia.geometry-analysis/v1"
    status: str
    source_format: str = "STEP_PART_21"
    unit: str
    bounding_box: BoundingBoxResponse | None
    surface_area: GeometryValue
    volume: GeometryValue
    topology_valid: bool | None
    tolerance: GeometryValue
    entity_count: int
    warnings: list[str]
    uncertainty: str
    traceability: list[str]
    kernel: str
    kernel_version: str | None
    limitations: list[str]


class GeometryKernelDecision(BaseModel):
    decision: str
    candidate: str
    license: str
    integration_status: str
    official_python: str
    experimental_python: str
    contract_schema: str
    limitations: list[str]
