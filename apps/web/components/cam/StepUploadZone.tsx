"use client";

import { useId, useRef, useState } from "react";
import { validateStepFile, type StepFileLike, type StepValidationResult } from "../../lib/cad-validation";

type UploadState = "idle" | "dragover" | "accepted" | "rejected";

type Props = Readonly<{
  maxSizeBytes?: number;
  onAccepted?: (file: File) => void;
  onCleared?: () => void;
}>;

function formatSize(sizeBytes: number): string {
  if (sizeBytes < 1024) return `${sizeBytes} B`;
  if (sizeBytes < 1024 * 1024) return `${(sizeBytes / 1024).toFixed(1)} KB`;
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`;
}

/** Client-only STEP picker. It validates in memory and does not send files over the network. */
export function StepUploadZone({ maxSizeBytes, onAccepted, onCleared }: Props) {
  const inputId = useId();
  const inputRef = useRef<HTMLInputElement>(null);
  const [state, setState] = useState<UploadState>("idle");
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("Arraste um arquivo STEP ou clique para selecionar.");

  async function inspect(candidate: File | null | undefined) {
    const result: StepValidationResult = await validateStepFile(candidate as StepFileLike | null | undefined, { maxSizeBytes });
    if (!result.valid || !candidate) {
      setFile(null);
      setState("rejected");
      setMessage(result.error ?? "O arquivo não foi aceito.");
      return;
    }
    setFile(candidate);
    setState("accepted");
    setMessage("Arquivo STEP validado localmente. Nenhum envio foi realizado.");
    onAccepted?.(candidate);
  }

  function clear() {
    setFile(null);
    setState("idle");
    setMessage("Arraste um arquivo STEP ou clique para selecionar.");
    if (inputRef.current) inputRef.current.value = "";
    onCleared?.();
  }

  const stateClasses = state === "dragover"
    ? "border-cyan-400 bg-cyan-950/40"
    : state === "accepted"
      ? "border-emerald-400 bg-emerald-950/30"
      : state === "rejected"
        ? "border-rose-400 bg-rose-950/30"
        : "border-slate-600 bg-slate-900";

  return <section aria-label="Envio local de arquivo STEP" className={`rounded-xl border-2 border-dashed p-6 text-slate-100 ${stateClasses}`}>
    <input ref={inputRef} id={inputId} type="file" accept=".step,.stp" className="sr-only"
      onChange={event => void inspect(event.target.files?.item(0))} />
    <div onDragEnter={event => { event.preventDefault(); setState("dragover"); }}
      onDragOver={event => event.preventDefault()}
      onDragLeave={event => { event.preventDefault(); if (!file) setState("idle"); }}
      onDrop={event => { event.preventDefault(); setState("idle"); void inspect(event.dataTransfer.files.item(0)); }}
      className="space-y-3 text-center">
      <p className="text-base font-semibold">Arquivo STEP local</p>
      <p aria-live="polite" className="text-sm text-slate-300">{message}</p>
      {file && <p className="text-sm"><span className="font-medium">{file.name}</span> · {formatSize(file.size)}</p>}
      <div className="flex flex-wrap justify-center gap-3">
        <label htmlFor={inputId} className="cursor-pointer rounded bg-cyan-700 px-4 py-2 text-sm font-medium hover:bg-cyan-600">
          Selecionar arquivo
        </label>
        {file && <button type="button" onClick={clear} className="rounded border border-slate-400 px-4 py-2 text-sm hover:bg-slate-800">Limpar</button>}
      </div>
      <p className="text-xs text-slate-400">Aceita .step e .stp. Validação local limitada; sem upload, rede ou geração de NC.</p>
    </div>
  </section>;
}
