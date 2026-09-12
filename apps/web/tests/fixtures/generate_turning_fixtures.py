"""Export actual E2E results; --check replays and validates committed TS payloads."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import runpy
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[4]
    sys.path.insert(0, str(root / "apps/api"))
    # Reuse precisely the real STEP/E2E setup; no hand-edited geometric payloads.
    suite = runpy.run_path(str(root / "apps/api/tests/modules/engineering/test_turning_pipeline_e2e.py"))
    inputs, run = suite["_inputs"], suite["_run"]
    zone = suite["TurningStaticExclusionZone"](
        zone_id="narrow-radial-band", r_min_mm=26.5004, r_max_mm=26.5006,
        z_min_mm=-60.0, z_max_mm=-50.0,
    )
    cases = [
        ("cylinder-success", "cylinderSuccess", run(), "SUCCESS_SYNTHETIC"),
        ("quantized-violation", "quantizedViolation", run(
            params=inputs()["params"].model_copy(update={"radial_allowance_mm": 0.50026}),
            exclusion_zones=(zone,),
        ), "QUANTIZED_BOUNDARY_VIOLATION"),
        ("reconstruction-failure", "reconstructionFailure", run(
            params=inputs()["params"].model_copy(update={
                "radial_allowance_mm": 9.99999, "clearance_mm": 0.00001,
            }),
        ), "QUANTIZED_VERIFICATION_FAILED"),
    ]
    for filename, variable, result, status in cases:
        assert result.pipeline_status == status
        validated = type(result).model_validate_json(result.model_dump_json())
        assert validated == result
        payload = json.dumps(result.model_dump(mode="json"), indent=2, allow_nan=False)
        text = (
            '// Generated from real Python E2E pipeline; see README.md. Never machine-ready.\n'
            'import type { SyntheticTurningExecutionResult } from "../../lib/turning-contracts";\n\n'
            f'export const {variable} = {payload} as const satisfies SyntheticTurningExecutionResult;\n'
        )
        path = Path(__file__).parent / f"{filename}.ts"
        if args.check:
            existing = path.read_text(encoding="utf-8")
            encoded = existing.split(f"export const {variable} = ", 1)[1].split(
                " as const satisfies", 1,
            )[0]
            assert type(result).model_validate_json(encoded) == result, filename
            assert existing == text, f"fixture drift: {filename}"
        else:
            path.write_text(text, encoding="utf-8")
        print(f"{filename}: {status}, Pydantic validation and {'replay' if args.check else 'export'} PASS")


if __name__ == "__main__":
    main()
