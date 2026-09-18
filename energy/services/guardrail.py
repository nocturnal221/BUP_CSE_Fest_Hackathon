"""Deterministic Guardrail Validator for LLM Directive Interpretations."""
from typing import List, Dict, Any

ALLOWED_DIRECTIVES = {
    "solar_reduction",
    "minimum_battery_reserve",
    "no_charge_window",
    "no_discharge_window",
    "max_grid_window",
    "no_op"
}


def _make_safe_noop(index: int, reason: str = "Invalid adjustment format; converted to no_op by guardrail.") -> Dict[str, Any]:
    return {
        "note_index": index,
        "applies": False,
        "directive_type": "no_op",
        "structured_adjustment": None,
        "explanation": reason
    }


def validate_directive_interpretation(
    raw_interpretations: List[Dict[str, Any]],
    expected_count: int,
    battery_info: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """
    Validates and sanitizes a list of directive interpretations.
    Never throws exceptions; converts malformed entries to safe no_ops.
    """
    validated: List[Dict[str, Any]] = []

    for i in range(expected_count):
        if i >= len(raw_interpretations) or not isinstance(raw_interpretations[i], dict):
            validated.append(_make_safe_noop(i, "Missing interpretation entry."))
            continue

        item = raw_interpretations[i]
        directive_type = item.get("directive_type")
        if directive_type not in ALLOWED_DIRECTIVES:
            validated.append(_make_safe_noop(i, f"Unknown directive type '{directive_type}'."))
            continue

        if directive_type == "no_op":
            validated.append({
                "note_index": i,
                "applies": False,
                "directive_type": "no_op",
                "structured_adjustment": None,
                "explanation": str(item.get("explanation") or "No operation required.")
            })
            continue

        # For active directives, validate structured_adjustment
        adj = item.get("structured_adjustment")
        if not isinstance(adj, dict):
            validated.append(_make_safe_noop(i, "Missing structured_adjustment for active directive."))
            continue

        hours = adj.get("hours")
        if not isinstance(hours, (list, tuple)) or len(hours) == 0:
            validated.append(_make_safe_noop(i, "Invalid or empty hours list."))
            continue

        # Check hours validity: integers in 0..23, unique, sorted
        try:
            int_hours = [int(h) for h in hours]
        except (ValueError, TypeError):
            validated.append(_make_safe_noop(i, "Hours must be valid integers."))
            continue

        if any(h < 0 or h > 23 for h in int_hours):
            validated.append(_make_safe_noop(i, "Hours must be between 0 and 23."))
            continue

        sorted_unique_hours = sorted(list(set(int_hours)))
        sanitized_adj: Dict[str, Any] = {"hours": sorted_unique_hours}

        # Directive-specific checks
        is_valid = True
        if directive_type == "solar_reduction":
            factor = adj.get("factor")
            if factor is None:
                is_valid = False
            else:
                try:
                    f_val = float(factor)
                    if 0.0 <= f_val <= 1.0:
                        sanitized_adj["factor"] = round(f_val, 4)
                    else:
                        is_valid = False
                except (ValueError, TypeError):
                    is_valid = False

        elif directive_type == "minimum_battery_reserve":
            min_energy = adj.get("minimum_energy_kwh")
            if min_energy is None:
                is_valid = False
            else:
                try:
                    m_val = float(min_energy)
                    if m_val >= 0.0:
                        sanitized_adj["minimum_energy_kwh"] = round(m_val, 2)
                    else:
                        is_valid = False
                except (ValueError, TypeError):
                    is_valid = False

        elif directive_type == "max_grid_window":
            max_grid = adj.get("max_grid_kwh")
            if max_grid is None:
                is_valid = False
            else:
                try:
                    g_val = float(max_grid)
                    if g_val >= 0.0:
                        sanitized_adj["max_grid_kwh"] = round(g_val, 2)
                    else:
                        is_valid = False
                except (ValueError, TypeError):
                    is_valid = False

        elif directive_type in ("no_charge_window", "no_discharge_window"):
            # Only hours needed
            pass

        if not is_valid:
            validated.append(_make_safe_noop(i, f"Invalid parameters for directive {directive_type}."))
            continue

        validated.append({
            "note_index": i,
            "applies": True,
            "directive_type": directive_type,
            "structured_adjustment": sanitized_adj,
            "explanation": str(item.get("explanation") or f"Applied {directive_type}.")
        })

    return validated
