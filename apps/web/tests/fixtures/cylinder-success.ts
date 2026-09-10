// Generated from real Python E2E pipeline; see README.md. Never machine-ready.
import type { SyntheticTurningExecutionResult } from "../../lib/turning-contracts";

export const cylinderSuccess = {
  "pipeline_status": "SUCCESS_SYNTHETIC",
  "failure_reason": null,
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
              36.0,
              4.0
            ],
            "end_point": [
              36.0,
              2.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
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
              4.0
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              0.0,
              4.0
            ],
            "end_point": [
              36.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              4.0
            ],
            "end_point": [
              36.0,
              1.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
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
              4.0
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              0.0,
              4.0
            ],
            "end_point": [
              36.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              4.0
            ],
            "end_point": [
              36.0,
              0.5
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
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
              4.0
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              0.0,
              4.0
            ],
            "end_point": [
              36.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          }
        ]
      },
      {
        "operation_id": "synthetic-longitudinal",
        "operation_type": "ROUGH_TURNING",
        "passes_count": 5,
        "moves": [
          {
            "start_point": [
              36.0,
              4.0
            ],
            "end_point": [
              33.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              33.0,
              4.0
            ],
            "end_point": [
              33.0,
              -100.0
            ],
            "motion_type": "CUTTING",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              33.0,
              -100.0
            ],
            "end_point": [
              36.0,
              -100.0
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              -100.0
            ],
            "end_point": [
              36.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              4.0
            ],
            "end_point": [
              31.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              31.0,
              4.0
            ],
            "end_point": [
              31.0,
              -100.0
            ],
            "motion_type": "CUTTING",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              31.0,
              -100.0
            ],
            "end_point": [
              36.0,
              -100.0
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              -100.0
            ],
            "end_point": [
              36.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              4.0
            ],
            "end_point": [
              29.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              29.0,
              4.0
            ],
            "end_point": [
              29.0,
              -100.0
            ],
            "motion_type": "CUTTING",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              29.0,
              -100.0
            ],
            "end_point": [
              36.0,
              -100.0
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              -100.0
            ],
            "end_point": [
              36.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              4.0
            ],
            "end_point": [
              27.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              27.0,
              4.0
            ],
            "end_point": [
              27.0,
              -100.0
            ],
            "motion_type": "CUTTING",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              27.0,
              -100.0
            ],
            "end_point": [
              36.0,
              -100.0
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              -100.0
            ],
            "end_point": [
              36.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              4.0
            ],
            "end_point": [
              25.5,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              25.5,
              4.0
            ],
            "end_point": [
              25.5,
              -100.0
            ],
            "motion_type": "CUTTING",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              25.5,
              -100.0
            ],
            "end_point": [
              36.0,
              -100.0
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              -100.0
            ],
            "end_point": [
              36.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          }
        ]
      }
    ],
    "total_cutting_length_mm": 628.0,
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
    "parameters_digest_sha256": "720b01f05fb3a0d051aea1be83a4058912cc69258e842e728837d107a92a63f2",
    "quantization_decimal_places": 3,
    "quantization_digest_sha256": "9d133ceebb27b5dcb4d8f905407ce1c0d5fea5944986a9b14b36936e55b8ca10",
    "quantized_verification_digest_sha256": "ff4ba043ec222df3e5f0afaa8c8a8968beb285ee18fb2157af75b4c0f7180ab9",
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
    "evaluated_moves_count": 32,
    "max_positive_radial_deviation_mm": 0.0,
    "max_negative_radial_deviation_mm": 0.0,
    "move_reports": [
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
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
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
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
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
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
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 33.0,
        "programmed_x_diameter_mm": 66.0,
        "reconstructed_radius_mm": 33.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 33.0,
        "programmed_x_diameter_mm": 66.0,
        "reconstructed_radius_mm": 33.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 33.0,
        "programmed_x_diameter_mm": 66.0,
        "reconstructed_radius_mm": 33.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 33.0,
        "programmed_x_diameter_mm": 66.0,
        "reconstructed_radius_mm": 33.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 31.0,
        "programmed_x_diameter_mm": 62.0,
        "reconstructed_radius_mm": 31.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 31.0,
        "programmed_x_diameter_mm": 62.0,
        "reconstructed_radius_mm": 31.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 31.0,
        "programmed_x_diameter_mm": 62.0,
        "reconstructed_radius_mm": 31.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 31.0,
        "programmed_x_diameter_mm": 62.0,
        "reconstructed_radius_mm": 31.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 29.0,
        "programmed_x_diameter_mm": 58.0,
        "reconstructed_radius_mm": 29.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 29.0,
        "programmed_x_diameter_mm": 58.0,
        "reconstructed_radius_mm": 29.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 29.0,
        "programmed_x_diameter_mm": 58.0,
        "reconstructed_radius_mm": 29.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 29.0,
        "programmed_x_diameter_mm": 58.0,
        "reconstructed_radius_mm": 29.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 27.0,
        "programmed_x_diameter_mm": 54.0,
        "reconstructed_radius_mm": 27.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 27.0,
        "programmed_x_diameter_mm": 54.0,
        "reconstructed_radius_mm": 27.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 27.0,
        "programmed_x_diameter_mm": 54.0,
        "reconstructed_radius_mm": 27.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 27.0,
        "programmed_x_diameter_mm": 54.0,
        "reconstructed_radius_mm": 27.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 25.5,
        "programmed_x_diameter_mm": 51.0,
        "reconstructed_radius_mm": 25.5,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 25.5,
        "programmed_x_diameter_mm": 51.0,
        "reconstructed_radius_mm": 25.5,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 25.5,
        "programmed_x_diameter_mm": 51.0,
        "reconstructed_radius_mm": 25.5,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 25.5,
        "programmed_x_diameter_mm": 51.0,
        "reconstructed_radius_mm": 25.5,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
        "is_boundary_safe": false,
        "boundary_status": "NOT_EVALUATED",
        "limitations": [
          "NUMERICAL_QUANTIZATION_CHECK_ONLY"
        ]
      },
      {
        "original_radius_mm": 36.0,
        "programmed_x_diameter_mm": 72.0,
        "reconstructed_radius_mm": 36.0,
        "radial_deviation_mm": 0.0,
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
  "quantized_plan": {
    "profile_id": "synthetic-profile:sha256:c0b54e996d884da3df732de98a1622622c6eaea15c8a102538269365636bb323",
    "operations": [
      {
        "operation_id": "synthetic-facing",
        "operation_type": "FACING",
        "passes_count": 3,
        "moves": [
          {
            "start_point": [
              36.0,
              4.0
            ],
            "end_point": [
              36.0,
              2.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
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
              4.0
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              0.0,
              4.0
            ],
            "end_point": [
              36.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              4.0
            ],
            "end_point": [
              36.0,
              1.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
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
              4.0
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              0.0,
              4.0
            ],
            "end_point": [
              36.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              4.0
            ],
            "end_point": [
              36.0,
              0.5
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
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
              4.0
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              0.0,
              4.0
            ],
            "end_point": [
              36.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          }
        ]
      },
      {
        "operation_id": "synthetic-longitudinal",
        "operation_type": "ROUGH_TURNING",
        "passes_count": 5,
        "moves": [
          {
            "start_point": [
              36.0,
              4.0
            ],
            "end_point": [
              33.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              33.0,
              4.0
            ],
            "end_point": [
              33.0,
              -100.0
            ],
            "motion_type": "CUTTING",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              33.0,
              -100.0
            ],
            "end_point": [
              36.0,
              -100.0
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              -100.0
            ],
            "end_point": [
              36.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              4.0
            ],
            "end_point": [
              31.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              31.0,
              4.0
            ],
            "end_point": [
              31.0,
              -100.0
            ],
            "motion_type": "CUTTING",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              31.0,
              -100.0
            ],
            "end_point": [
              36.0,
              -100.0
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              -100.0
            ],
            "end_point": [
              36.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              4.0
            ],
            "end_point": [
              29.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              29.0,
              4.0
            ],
            "end_point": [
              29.0,
              -100.0
            ],
            "motion_type": "CUTTING",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              29.0,
              -100.0
            ],
            "end_point": [
              36.0,
              -100.0
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              -100.0
            ],
            "end_point": [
              36.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              4.0
            ],
            "end_point": [
              27.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              27.0,
              4.0
            ],
            "end_point": [
              27.0,
              -100.0
            ],
            "motion_type": "CUTTING",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              27.0,
              -100.0
            ],
            "end_point": [
              36.0,
              -100.0
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              -100.0
            ],
            "end_point": [
              36.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              4.0
            ],
            "end_point": [
              25.5,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              25.5,
              4.0
            ],
            "end_point": [
              25.5,
              -100.0
            ],
            "motion_type": "CUTTING",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              25.5,
              -100.0
            ],
            "end_point": [
              36.0,
              -100.0
            ],
            "motion_type": "RETRACT",
            "feed_rate_type": "MM_PER_REVOLUTION"
          },
          {
            "start_point": [
              36.0,
              -100.0
            ],
            "end_point": [
              36.0,
              4.0
            ],
            "motion_type": "RAPID",
            "feed_rate_type": "MM_PER_REVOLUTION"
          }
        ]
      }
    ],
    "total_cutting_length_mm": 628.0,
    "is_collision_free": false,
    "collision_status": "NOT_VALIDATED",
    "executable_output": false,
    "physical_use_authorized": false
  },
  "quantized_verification": {
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
  "is_physical_ready": false,
  "physical_use_authorized": false,
  "executable_output": false,
  "emission_status": "CONTROLLER_PROFILE_UNRESOLVED"
} as const satisfies SyntheticTurningExecutionResult;
