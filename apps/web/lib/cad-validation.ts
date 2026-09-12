export type StepValidationResult = Readonly<{
  valid: boolean;
  error?: string;
  metadata?: Readonly<{ sizeBytes: number; filename: string }>;
}>;

export type StepFileLike = Readonly<{
  name: string;
  size: number;
  slice(start?: number, end?: number): Readonly<{ text(): Promise<string> }>;
}>;

export type StepValidationOptions = Readonly<{
  maxSizeBytes?: number;
  headerBytes?: number;
}>;

export const DEFAULT_STEP_MAX_SIZE_BYTES = 15 * 1024 * 1024;
const DEFAULT_HEADER_BYTES = 8 * 1024;

function rejected(error: string): StepValidationResult {
  return { valid: false, error };
}

function isStepFilename(filename: string): boolean {
  return /\.(step|stp)$/i.test(filename.trim());
}

/**
 * Performs bounded, client-only STEP validation. It reads only a small header slice
 * after rejecting invalid names and sizes, and never uploads or retains the file.
 */
export async function validateStepFile(
  file: StepFileLike | null | undefined,
  options: StepValidationOptions = {},
): Promise<StepValidationResult> {
  const maxSizeBytes = options.maxSizeBytes ?? DEFAULT_STEP_MAX_SIZE_BYTES;
  const headerBytes = options.headerBytes ?? DEFAULT_HEADER_BYTES;

  if (!file) return rejected("Selecione um arquivo STEP.");
  if (!Number.isSafeInteger(file.size) || file.size <= 0) return rejected("O arquivo STEP está vazio ou possui tamanho inválido.");
  if (!Number.isSafeInteger(maxSizeBytes) || maxSizeBytes <= 0) return rejected("O limite de tamanho configurado é inválido.");
  if (!Number.isSafeInteger(headerBytes) || headerBytes <= 0) return rejected("O limite de inspeção de cabeçalho é inválido.");
  if (!isStepFilename(file.name)) return rejected("Use um arquivo com extensão .step ou .stp.");
  if (file.size > maxSizeBytes) return rejected(`O arquivo excede o limite de ${maxSizeBytes} bytes.`);

  try {
    const header = await file.slice(0, Math.min(file.size, headerBytes)).text();
    if (!header.includes("ISO-10303-21;") || !header.includes("HEADER;")) {
      return rejected("O arquivo não possui um cabeçalho ISO-10303-21 STEP válido.");
    }
  } catch {
    return rejected("Não foi possível inspecionar o cabeçalho do arquivo STEP.");
  }

  return { valid: true, metadata: { sizeBytes: file.size, filename: file.name } };
}
