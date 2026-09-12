export type StepGeometryFileLike = Readonly<{
  name: string;
  size: number;
  slice(start?: number, end?: number): Readonly<{ text(): Promise<string> }>;
}>;

export type TurningProfileDTO = Readonly<{
  source: "STEP_TEXTUAL_METADATA_ONLY";
  points: readonly [];
  visualizable: false;
  limitations: readonly ["NO_GEOMETRY_EXTRACTION", "ASYNC_ANALYSIS_REQUIRED"];
}>;

export type StepGeometryMetadata = Readonly<{
  schema: "AP203" | "AP214" | "AP242" | "UNKNOWN";
  applicationIdentifier: string | null;
  lengthUnit: "MILLIMETRE" | "METRE" | "UNKNOWN";
  bytesRead: number;
}>;

export type StepGeometryInspection =
  | Readonly<{ supported: true; metadata: StepGeometryMetadata; profile: TurningProfileDTO }>
  | Readonly<{ supported: false; reason: "Geometria B-Rep sólida não identificada no cabeçalho textual"; metadata: StepGeometryMetadata }>;

const HEADER_BYTES = 64 * 1024;
const solidTokens = ["MANIFOLD_SOLID_BREP", "CLOSED_SHELL", "ADVANCED_FACE"];

function extractSchema(text: string): StepGeometryMetadata["schema"] {
  const match = text.match(/\b(AP203|AP214|AP242)\b/i);
  return match ? match[1].toUpperCase() as StepGeometryMetadata["schema"] : "UNKNOWN";
}

function extractUnit(text: string): StepGeometryMetadata["lengthUnit"] {
  if (/\bMILLIMETRE\b|\.MILLI\.\s*,\s*\.METRE\./i.test(text)) return "MILLIMETRE";
  if (/\bMETRE\b/i.test(text)) return "METRE";
  return "UNKNOWN";
}

/**
 * Bounded client-only textual inspection. This is not CAD geometry extraction and
 * never manufactures points for the synthetic viewer from a STEP payload.
 */
export async function inspectStepGeometry(file: StepGeometryFileLike): Promise<StepGeometryInspection> {
  const bytesRead = Math.min(file.size, HEADER_BYTES);
  const text = await file.slice(0, bytesRead).text();
  const applicationIdentifier = text.match(/APPLICATION_PROTOCOL_DEFINITION\s*\(\s*'([^']+)'/i)?.[1] ?? null;
  const metadata: StepGeometryMetadata = {
    schema: extractSchema(text), applicationIdentifier, lengthUnit: extractUnit(text), bytesRead,
  };
  if (!solidTokens.some(token => text.includes(token))) {
    return { supported: false, reason: "Geometria B-Rep sólida não identificada no cabeçalho textual", metadata };
  }
  return {
    supported: true,
    metadata,
    profile: {
      source: "STEP_TEXTUAL_METADATA_ONLY", points: [], visualizable: false,
      limitations: ["NO_GEOMETRY_EXTRACTION", "ASYNC_ANALYSIS_REQUIRED"],
    },
  };
}
