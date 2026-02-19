import re
from collections import Counter
from typing import Any

PLACEHOLDER_REGEX = re.compile(r"^\{\{[a-zA-Z0-9_]+\}\}$")

REQUIRED_FIELDS: dict[str, dict[str, str]] = {
    "PRODUCT": {
        "{{headline}}": "TEXT",
        "{{price}}": "TEXT",
        "{{cta}}": "TEXT",
        "{{image_main}}": "IMAGE",
    },
    "BLOG": {
        "{{headline}}": "TEXT",
        "{{slide_title}}": "TEXT",
        "{{slide_body}}": "TEXT",
        "{{image_main}}": "IMAGE",
    },
    "CAMPAIGN": {
        "{{headline}}": "TEXT",
        "{{cta}}": "TEXT",
    },
    "PARTNER": {
        "{{headline}}": "TEXT",
        "{{partner_logo}}": "IMAGE",
    },
    "EVENT": {
        "{{headline}}": "TEXT",
        "{{date}}": "TEXT",
        "{{cta}}": "TEXT",
    },
}


def validate_template_contract(template_type: str, placeholders: list[dict[str, Any]]) -> dict[str, Any]:
    required = REQUIRED_FIELDS[template_type]
    extracted_names = [entry["placeholder"] for entry in placeholders]

    invalid_format = [name for name in extracted_names if not PLACEHOLDER_REGEX.match(name)]
    duplicates = [name for name, count in Counter(extracted_names).items() if count > 1]

    missing_required = [name for name in required if name not in extracted_names]

    node_type_mismatches: list[dict[str, str]] = []
    by_name = {entry["placeholder"]: entry for entry in placeholders}

    for required_name, required_kind in required.items():
        detected = by_name.get(required_name)
        if not detected:
            continue
        if detected.get("node_kind") != required_kind:
            node_type_mismatches.append(
                {
                    "placeholder": required_name,
                    "required_kind": required_kind,
                    "detected_kind": detected.get("node_kind", "UNKNOWN"),
                }
            )

    passed = not any([invalid_format, duplicates, missing_required, node_type_mismatches])
    return {
        "passed": passed,
        "invalid_format": invalid_format,
        "duplicates": duplicates,
        "missing_required": missing_required,
        "node_type_mismatches": node_type_mismatches,
        "required_placeholders": required,
    }
