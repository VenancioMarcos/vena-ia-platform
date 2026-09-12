// Generated from real Python E2E pipeline; see README.md. Never machine-ready.
import type { SyntheticTurningExecutionResult } from "../../lib/turning-contracts";

export const reconstructionFailure = {
  "pipeline_status": "QUANTIZED_VERIFICATION_FAILED",
  "failure_reason": "QUANTIZED_RECONSTRUCTION_OR_VERIFICATION_FAILED",
  "profile": {
    "points": [
      {
        "radius_mm": 0.0,
        "z_mm": 0.0
      },
      {
        "radius_mm": 25.0,
        "z_mm": 0.0
      },
      {
        "radius_mm": 25.0,
        "z_mm": -100.0
      },
      {
        "radius_mm": 0.0,
        "z_mm": -100.0
      }
    ],
    "axis_origin": [
      0.0,
      0.0,
      0.0
    ],
    "axis_direction": [
      0.0,
      0.0,
      1.0
    ],
    "is_closed": false
  },
  "plan": {
    "profile_id": "synthetic-profile:sha256:c0b54e996d884da3df732de98a1622622c6eaea15c8a102538269365636bb323",
    "operations": [
      {
        "operation_id": "synthetic-facing",
        "operation_type": "FACING",
        "passes_count": 3,
        "moves": [
          {
            "start_point": [
              35.00001,
              3.00001
            ],
            "end_point": [
              35.00001,
              2.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              35.00001,
              2.0
            ],
            "end_point": [
              0.0,
              2.0
            ],
            "motion_type": "CUTTING",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              0.0,
              2.0
            ],
            "end_point": [
              0.0,
              3.00001
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              0.0,
              3.00001
            ],
            "end_point": [
              35.00001,
              3.00001
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              35.00001,
              3.00001
            ],
            "end_point": [
              35.00001,
              1.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              35.00001,
              1.0
            ],
            "end_point": [
              0.0,
              1.0
            ],
            "motion_type": "CUTTING",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              0.0,
              1.0
            ],
            "end_point": [
              0.0,
              3.00001
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              0.0,
              3.00001
            ],
            "end_point": [
              35.00001,
              3.00001
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              35.00001,
              3.00001
            ],
            "end_point": [
              35.00001,
              0.5
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              35.00001,
              0.5
            ],
            "end_point": [
              0.0,
              0.5
            ],
            "motion_type": "CUTTING",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              0.0,
              0.5
            ],
            "end_point": [
              0.0,
              3.00001
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              0.0,
              3.00001
            ],
            "end_point": [
              35.00001,
              3.00001
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          }
        ]
      },
      {
        "operation_id": "synthetic-longitudinal",
        "operation_type": "ROUGH_TURNING",
        "passes_count": 1,
        "moves": [
          {
            "start_point": [
              35.00001,
              3.00001
            ],
            "end_point": [
              34.99999,
              3.00001
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              34.99999,
              3.00001
            ],
            "end_point": [
              34.99999,
              -100.0
            ],
            "motion_type": "CUTTING",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              34.99999,
              -100.0
            ],
            "end_point": [
              35.00001,
              -100.0
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              35.00001,
              -100.0
            ],
            "end_point": [
              35.00001,
              3.00001
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          }
        ]
      }
    ],
    "total_cutting_length_mm": 208.00004,
    "is_collision_free": false,
    "collision_status": "NOT_VALIDATED",
    "executable_output": false,
    "physical_use_authorized": false
  },
  "verification": {
    "boundary_status": "PASS",
    "declared_boundaries_passed": true,
    "violating_moves": [],
    "is_verified": false,
    "collision_status": "NOT_VALIDATED",
    "executable_output": false,
    "physical_use_authorized": false,
    "limitations": [
      "NO_STOCK_OR_MATERIAL_REMOVAL_VALIDATION",
      "NO_REAL_TOOL_OR_FIXTURE_VALIDATION"
    ]
  },
  "metadata": {
    "schema_version": "synthetic-turning/v3",
    "evaluated_at_utc": "2026-09-09T00:00:00Z",
    "parameters_digest_sha256": "2719fca147fa77acd3d8aa71ced4ca83b8a1a3c8f6aa369cbb6972eec4fa1153",
    "quantization_decimal_places": 3,
    "quantization_digest_sha256": "b10e2623dfc5c77e5902fff1a32a13ff46a30ca976913c3e8c25842e7cb507ab",
    "quantized_verification_digest_sha256": null,
    "brep_serialization_digest_sha256": "f42c1d393a5b002156c854a0d144309760ba8efdf544cecc640e7c611bd3f38c",
    "brep_serialization_format": "OCCT_BREP_ASCII_V3_NO_TRIANGLES_NO_NORMALS",
    "occt_binding_version": "7.9.3.1.1",
    "limitations": [
      "NO_CANONICAL_GEOMETRIC_IDENTITY",
      "NO_DIGITAL_THREAD_INTEGRATION",
      "NO_PHYSICAL_AUTHORITY"
    ]
  },
  "quantization": {
    "decimal_places": 3,
    "evaluated_moves_count": 16,
    "max_positive_radial_deviation_mm": 1.0000000003174137e-05,
    "max_negative_radial_deviation_mm": -1.0000000003174137e-05,
    "move_reports": [
      {
        "original_radius_mm": 35.00001,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": -1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 35.00001,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": -1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 35.00001,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": -1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 0.0,
        "programmed_x_diameter_mm": 0.0,
        "reconstructed_radius_mm": 0.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 0.0,
        "programmed_x_diameter_mm": 0.0,
        "reconstructed_radius_mm": 0.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 0.0,
        "programmed_x_diameter_mm": 0.0,
        "reconstructed_radius_mm": 0.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 0.0,
        "programmed_x_diameter_mm": 0.0,
        "reconstructed_radius_mm": 0.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 35.00001,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": -1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 35.00001,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": -1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 35.00001,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": -1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 35.00001,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": -1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 0.0,
        "programmed_x_diameter_mm": 0.0,
        "reconstructed_radius_mm": 0.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 0.0,
        "programmed_x_diameter_mm": 0.0,
        "reconstructed_radius_mm": 0.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 0.0,
        "programmed_x_diameter_mm": 0.0,
        "reconstructed_radius_mm": 0.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 0.0,
        "programmed_x_diameter_mm": 0.0,
        "reconstructed_radius_mm": 0.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 35.00001,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": -1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 35.00001,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": -1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 35.00001,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": -1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 35.00001,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": -1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 0.0,
        "programmed_x_diameter_mm": 0.0,
        "reconstructed_radius_mm": 0.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 0.0,
        "programmed_x_diameter_mm": 0.0,
        "reconstructed_radius_mm": 0.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 0.0,
        "programmed_x_diameter_mm": 0.0,
        "reconstructed_radius_mm": 0.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 0.0,
        "programmed_x_diameter_mm": 0.0,
        "reconstructed_radius_mm": 0.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 35.00001,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": -1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 35.00001,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": -1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 34.99999,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": 1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 34.99999,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": 1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 34.99999,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": 1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 34.99999,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": 1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 35.00001,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": -1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 35.00001,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": -1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 35.00001,
        "programmed_x_diameter_mm": 70.0,
        "reconstructed_radius_mm": 35.0,
        "radial_deviation_mm": -1.0000000003174137e-05,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      }
    ],
    "is_boundary_safe": false,
    "boundary_status": "NOT_EVALUATED",
    "limitations": [
      "NUMERICAL_QUANTIZATION_AGGREGATE_ONLY"
    ]
  },
  "quantized_plan": null,
  "quantized_verification": null,
  "is_physical_ready": false,
  "physical_use_authorized": false,
  "executable_output": false,
  "emission_status": "CONTROLLER_PROFILE_UNRESOLVED"
} as const satisfies SyntheticTurningExecutionResult;
