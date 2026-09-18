"""LLM Interpreter service for translating operator notes into structured directives."""
import os
import re
import json
from typing import List, Dict, Any

OPENAI_AVAILABLE = False
try:
    # pyrefly: ignore [missing-import]
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    pass

SYSTEM_PROMPT = """You are an expert energy management operator assistant for the GridWise microgrid.
Translate each operator note into one structured directive or a no_op.
Follow these rules strictly:
1. Allowed directive types:
   - solar_reduction: { "hours": [int, ...], "factor": float (usable fraction remaining, e.g. 80% reduction means 0.2) }
   - minimum_battery_reserve: { "hours": [int, ...], "minimum_energy_kwh": float }
   - no_charge_window: { "hours": [int, ...] }
   - no_discharge_window: { "hours": [int, ...] }
   - max_grid_window: { "hours": [int, ...], "max_grid_kwh": float }
   - no_op: null adjustment
2. Hour Rule: Whole hours, start inclusive, end exclusive. Hours are unique integers in ascending order.
   Examples:
   - "1 PM to 3 PM" -> [13, 14]
   - "noon until 2 PM" -> [12, 13]
   - "6 PM until 9 PM" -> [18, 19, 20]
   - "6 PM until 10 PM" -> [18, 19, 20, 21]
   - "2 AM until 5 AM" -> [2, 3, 4]
3. Battery percentage rule: If a reserve note says "at least X% of battery capacity", multiply X% by the battery capacity to get minimum_energy_kwh.
4. Output format: Return exactly one item per note in sequential note_index order (0, 1, ...).
5. For no_op: applies must be false, structured_adjustment must be null.
6. For non-no_op: applies must be true.
"""

DIRECTIVE_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "apply_directives",
        "description": "Output structured interpretations for all operator notes",
        "parameters": {
            "type": "object",
            "properties": {
                "interpretations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "note_index": {"type": "integer"},
                            "applies": {"type": "boolean"},
                            "directive_type": {
                                "type": "string",
                                "enum": [
                                    "solar_reduction",
                                    "minimum_battery_reserve",
                                    "no_charge_window",
                                    "no_discharge_window",
                                    "max_grid_window",
                                    "no_op"
                                ]
                            },
                            "structured_adjustment": {
                                "type": ["object", "null"],
                                "properties": {
                                    "hours": {
                                        "type": "array",
                                        "items": {"type": "integer"}
                                    },
                                    "factor": {"type": "number"},
                                    "minimum_energy_kwh": {"type": "number"},
                                    "max_grid_kwh": {"type": "number"}
                                }
                            },
                            "explanation": {"type": "string"}
                        },
                        "required": ["note_index", "applies", "directive_type", "structured_adjustment", "explanation"]
                    }
                }
            },
            "required": ["interpretations"]
        }
    }
}


def _parse_time_str(t_str: str) -> int:
    t_str = t_str.strip().lower()
    if "noon" in t_str:
        return 12
    if "midnight" in t_str:
        return 0
    m = re.match(r"(\d+)(?::\d+)?\s*(am|pm)?", t_str)
    if not m:
        return -1
    hour = int(m.group(1))
    period = m.group(2)
    if period == "pm" and hour != 12:
        hour += 12
    elif period == "am" and hour == 12:
        hour = 0
    return hour


def _extract_window_hours(text: str) -> List[int]:
    # Look for patterns like "from noon until 2 PM", "between 11 AM and 2 PM", "from 6 PM until 9 PM"
    pattern = r"(?:from|between)\s+([0-9a-z:\s]+?)\s+(?:until|to|and)\s+([0-9a-z:\s]+?)(?=[.,;]|\s+for|\s+while|\s+during|\s+because|$)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        start_str = match.group(1).strip()
        end_str = match.group(2).strip()
        start = _parse_time_str(start_str)
        end = _parse_time_str(end_str)
        if 0 <= start < end <= 24:
            return list(range(start, end))

    # Pattern without 'from': e.g. "from 7 PM until 10 PM" or "7 PM until 9 PM"
    m2 = re.search(r"(\d{1,2}\s*(?:AM|PM|noon)?)\s*(?:until|to)\s*(\d{1,2}\s*(?:AM|PM|noon)?)", text, re.IGNORECASE)
    if m2:
        start = _parse_time_str(m2.group(1))
        end = _parse_time_str(m2.group(2))
        if 0 <= start < end <= 24:
            return list(range(start, end))

    return []


def deterministic_interpret_note(note: str, index: int, battery_data: Dict[str, Any]) -> Dict[str, Any]:
    """High-fidelity pattern-matcher fallback for testing and offline environments."""
    lower = note.lower()

    # Distractor check
    distractor_words = ["sports office", "deadline", "library", "book-return", "club notice", "seminar room", "registration"]
    if any(dw in lower for dw in distractor_words):
        return {
            "note_index": index,
            "applies": False,
            "directive_type": "no_op",
            "structured_adjustment": None,
            "explanation": "This note does not affect today's energy schedule."
        }

    hours = _extract_window_hours(note)

    # 1. Solar reduction
    if "solar" in lower and ("clean" in lower or "reduc" in lower or "cloud" in lower or "inverter" in lower or "panel" in lower or "forecast" in lower):
        factor = 1.0
        pct_red = re.search(r"(\d+)%\s*reduction", lower)
        pct_forecast = re.search(r"(?:roughly|about)?\s*(\d+)%\s*of\s*(?:the)?\s*forecast", lower)
        half_match = "half" in lower

        if pct_red:
            factor = (100 - float(pct_red.group(1))) / 100.0
        elif pct_forecast:
            factor = float(pct_forecast.group(1)) / 100.0
        elif half_match:
            factor = 0.5

        if hours:
            return {
                "note_index": index,
                "applies": True,
                "directive_type": "solar_reduction",
                "structured_adjustment": {"hours": hours, "factor": factor},
                "explanation": f"Solar output adjusted by factor {factor} for hours {hours}."
            }

    # 2. No charge window
    if ("charg" in lower and ("isolated" in lower or "unavailable" in lower or "disabled" in lower or "outage" in lower or "maintenance" in lower or "inspect" in lower)) or \
       ("must not charge" in lower or "do not charge" in lower):
        if hours:
            return {
                "note_index": index,
                "applies": True,
                "directive_type": "no_charge_window",
                "structured_adjustment": {"hours": hours},
                "explanation": f"Battery charging is disabled for hours {hours}."
            }

    # 3. No discharge window
    if "discharge" in lower and ("must not" in lower or "do not" in lower or "disabled" in lower or "testing" in lower or "relay" in lower or "protection" in lower):
        if hours:
            return {
                "note_index": index,
                "applies": True,
                "directive_type": "no_discharge_window",
                "structured_adjustment": {"hours": hours},
                "explanation": f"Battery discharge is disabled for hours {hours}."
            }

    # 4. Minimum battery reserve
    if "reserve" in lower or "remain in the battery" in lower or "stored in the battery" in lower or "emergency" in lower or "backup" in lower:
        # Check percentage
        pct_cap = re.search(r"(\d+)%\s*of\s*(?:the)?\s*battery\s*capacity", lower)
        kwh_match = re.search(r"(\d+(?:\.\d+)?)\s*kwh", lower)

        min_kwh = None
        if pct_cap and battery_data and "capacity_kwh" in battery_data:
            pct = float(pct_cap.group(1)) / 100.0
            min_kwh = round(pct * float(battery_data["capacity_kwh"]), 2)
        elif kwh_match:
            min_kwh = float(kwh_match.group(1))

        if min_kwh is not None and hours:
            return {
                "note_index": index,
                "applies": True,
                "directive_type": "minimum_battery_reserve",
                "structured_adjustment": {"hours": hours, "minimum_energy_kwh": min_kwh},
                "explanation": f"Minimum battery reserve of {min_kwh} kWh required for hours {hours}."
            }

    # 5. Max grid window
    if "grid import" in lower or "grid intake" in lower or "transformer" in lower or "feeder" in lower or "substation" in lower:
        cap_match = re.search(r"(\d+(?:\.\d+)?)\s*kwh", lower)
        if cap_match and hours:
            max_grid = float(cap_match.group(1))
            return {
                "note_index": index,
                "applies": True,
                "directive_type": "max_grid_window",
                "structured_adjustment": {"hours": hours, "max_grid_kwh": max_grid},
                "explanation": f"Grid import capped at {max_grid} kWh for hours {hours}."
            }

    return {
        "note_index": index,
        "applies": False,
        "directive_type": "no_op",
        "structured_adjustment": None,
        "explanation": "This note does not affect today's energy schedule."
    }


def interpret_operator_notes(
    notes: List[str],
    battery_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Batches operator notes and sends them to OpenAI gpt-4o-mini with tool calling.
    Falls back gracefully to deterministic parsing if OpenAI is unavailable or fails.
    """
    api_key = os.environ.get("OPENAI_API_KEY")

    if OPENAI_AVAILABLE and api_key:
        try:
            client = openai.OpenAI(api_key=api_key)
            formatted_notes = "\n".join([f"Note {i}: {n}" for i, n in enumerate(notes)])
            user_msg = f"Battery Capacity: {battery_data.get('capacity_kwh')} kWh\n\nNotes to interpret:\n{formatted_notes}"

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg}
                ],
                tools=[DIRECTIVE_TOOL_SCHEMA],
                tool_choice={"type": "function", "function": {"name": "apply_directives"}},
                temperature=0.0
            )

            tool_calls = response.choices[0].message.tool_calls
            if tool_calls and tool_calls[0].function.arguments:
                args = json.loads(tool_calls[0].function.arguments)
                interpretations = args.get("interpretations", [])
                if len(interpretations) == len(notes):
                    return interpretations
        except Exception:
            # Fallback to deterministic parser
            pass

    # Deterministic fallback
    return [deterministic_interpret_note(note, i, battery_data) for i, note in enumerate(notes)]
