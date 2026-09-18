# GridWise — Smart Campus Energy Optimization System (Django + DRF + OpenAI)

BUP CSE FEST 2026 — Smart Campus Energy Optimization Challenge  
Version: 2.0 (LLM-Assisted Decision & Linear Optimization Pipeline)

---

## Architecture Overview

GridWise is an end-to-end intelligent energy optimization service designed for microgrids. It ingests 24-hour campus energy forecasts (demand, solar, time-of-use tariffs), battery storage parameters, and 1–3 unstructured natural language operator notes. It outputs an optimal 24-hour hourly schedule minimizing total grid import cost while respecting all physical, operational, and operator-dictated constraints.

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 POST /optimize-energy                  │
                  └───────────────────────────┬────────────────────────────┘
                                              │
                                              ▼
                         [1] Request Schema Validation (DRF)
                                              │
                                              ▼
                        [2] Operator Notes LLM Interpreter
                                (OpenAI gpt-4o-mini)
                                              │
                                              ▼
                          [3] Deterministic Guardrail Check
                             (Safe fail-back to no_op)
                                              │
                                              ▼
                           [4] Linear Programming Optimizer
                                 (Google OR-Tools GLOP)
                                              │
                                              ▼
                           [5] Independent Replay Validator
                                (Constraint Verification)
                                              │
                                              ▼
                                 HTTP 200 JSON Response
```

---

## 01 — API Endpoints & Contracts

### 1. `GET /health`
Returns quick service health status for load balancers and judge liveness probes.
- **Response**: `{"status": "ok"}` (HTTP 200)

### 2. `POST /optimize-energy`
The primary optimization pipeline endpoint.

#### Request Schema
```json
{
  "scenario_id": "SAMPLE-01",
  "operator_notes": [
    "Facilities will wash the rooftop solar panels from noon until 2 PM. During cleaning, usable solar should be treated as roughly 25% of the forecast.",
    "The sports office moved next month's registration deadline."
  ],
  "hours": [
    {
      "hour": 0,
      "demand_kwh": 90.0,
      "solar_kwh": 0.0,
      "tariff_bdt_per_kwh": 6.0
    }
    // ... exactly 24 entries, hours 0 to 23
  ],
  "battery": {
    "capacity_kwh": 220.0,
    "initial_energy_kwh": 110.0,
    "minimum_energy_kwh": 40.0,
    "max_charge_kwh_per_hour": 50.0,
    "max_discharge_kwh_per_hour": 50.0
  }
}
```

#### Response Schema
```json
{
  "scenario_id": "SAMPLE-01",
  "directive_interpretation": [
    {
      "note_index": 0,
      "applies": true,
      "directive_type": "solar_reduction",
      "structured_adjustment": {
        "hours": [12, 13],
        "factor": 0.25
      },
      "explanation": "Solar availability is reduced to 25% during the panel-cleaning window."
    },
    {
      "note_index": 1,
      "applies": false,
      "directive_type": "no_op",
      "structured_adjustment": null,
      "explanation": "This note does not affect today's 24-hour energy schedule."
    }
  ],
  "hourly_plan": [
    {
      "hour": 0,
      "grid_kwh": 90.0,
      "solar_used_kwh": 0.0,
      "battery_action": "idle",
      "battery_kwh": 0.0,
      "battery_energy_after_kwh": 110.0
    }
    // ... exactly 24 entries, hours 0 to 23
  ],
  "total_grid_kwh": 2692.5,
  "total_cost_bdt": 38365.0,
  "peak_grid_kwh": 175.0,
  "plan_summary": "Uses reduced midday solar availability, ignores distractor notes, and shifts battery energy toward higher-tariff hours while restoring initial battery level."
}
```

---

## 02 — Directive Types & Mathematical Effect

The LLM is constrained to map each note into one of exactly six recognized directive types:

| Directive | Structured Adjustment Shape | Mathematical Effect on LP |
|---|---|---|
| `solar_reduction` | `{"hours": [int, ...], "factor": float}` | $effective\_solar[h] = solar[h] \times factor$<br>$0 \le solar\_used[h] \le effective\_solar[h]$ |
| `minimum_battery_reserve` | `{"hours": [int, ...], "minimum_energy_kwh": float}` | $battery\_energy\_after[h] \ge \max(base\_min, minimum\_energy\_kwh)$ |
| `no_charge_window` | `{"hours": [int, ...]}` | $charge[h] = 0$ |
| `no_discharge_window` | `{"hours": [int, ...]}` | $discharge[h] = 0$ |
| `max_grid_window` | `{"hours": [int, ...], "max_grid_kwh": float}` | $grid[h] \le max\_grid\_kwh$ |
| `no_op` | `null` | No constraint change ($applies = false$) |

### Interpretation Rules
1. **Window Rule**: Time windows are start-inclusive and end-exclusive.
   - `"1 PM to 3 PM"` $\to$ hours `[13, 14]`
   - `"noon until 2 PM"` $\to$ hours `[12, 13]`
   - `"6 PM until 9 PM"` $\to$ hours `[18, 19, 20]`
   - `"6 PM until 10 PM"` $\to$ hours `[18, 19, 20, 21]`
2. **Solar Factor Rule**: `factor` is the usable remaining fraction:
   - `"80% reduction"` $\to$ `factor = 0.2`
   - `"usable solar is roughly 25%"` $\to$ `factor = 0.25`
   - `"about half"` $\to$ `factor = 0.5`
3. **Percentage Reserve Rule**: If reserve is specified as a percentage of battery capacity (e.g. 50% of 200 kWh), it is converted to absolute kWh (`100.0`).
4. **Ordering & Coverage**: Exactly one interpretation object per operator note, strictly in `note_index` order (`0, 1, ...`).

---

## 03 — LLM Integration & Deterministic Guardrails

### LLM Strategy (OpenAI Structured Tool Calling)
- All 1–3 operator notes are sent in a single batched prompt with the battery capacity context.
- Uses OpenAI tool calling (`function_calling`) or Structured Outputs (`response_format` with strict JSON schema).
- Negative constraints explicitly enforce:
  - Do not hallucinate numbers or directive types outside the 6 allowed.
  - Set `applies = false` and `structured_adjustment = null` on all `no_op` entries.
  - Set `applies = true` on any non-`no_op` directive.

### Guardrail Validator
Deterministic Python rules run immediately after LLM interpretation:
- Verify list length equals note count.
- Verify `note_index` is contiguous 0-indexed.
- Verify `hours` are unique integers in $[0, 23]$ sorted in ascending order.
- Verify `factor` $\in [0.0, 1.0]$.
- Verify `minimum_energy_kwh` $\ge 0$ and `max_grid_kwh` $\ge 0$.
- Any malformed interpretation is converted to a safe `no_op` rather than crashing the request.

---

## 04 — Mathematical Optimizer (LP Formulation)

Formulated and solved using Google OR-Tools (`pywraplp.Solver.GLOP_LINEAR_PROGRAMMING`).

### Decision Variables ($h \in [0, 23]$):
- $G_h \ge 0$: Grid draw (kWh)
- $S_h \ge 0$: Solar energy used (kWh)
- $C_h \ge 0$: Battery energy charged (kWh)
- $D_h \ge 0$: Battery energy discharged (kWh)
- $E_h \ge 0$: Battery energy level at the end of hour $h$ (kWh)

### Objective Function:
$$\min \sum_{h=0}^{23} G_h \cdot \text{tariff}_h$$

### Constraints:
1. **Solar Limit**:
   $$0 \le S_h \le \text{effective\_solar}_h \quad \forall h$$
2. **Campus Energy Balance**:
   $$G_h + S_h + D_h = \text{demand}_h + C_h \quad \forall h$$
3. **Battery Energy State Transition**:
   $$E_0 = \text{initial\_energy} + C_0 - D_0$$
   $$E_h = E_{h-1} + C_h - D_h \quad \forall h \in [1, 23]$$
4. **Battery Energy Bounds**:
   $$\max(\text{minimum\_energy}, \text{directive\_min}_h) \le E_h \le \text{capacity} \quad \forall h$$
5. **Battery Hourly Rate Limits**:
   $$0 \le C_h \le \text{max\_charge} \quad (C_h = 0 \text{ if no\_charge\_window})$$
   $$0 \le D_h \le \text{max\_discharge} \quad (D_h = 0 \text{ if no\_discharge\_window})$$
6. **Grid Import Limit**:
   $$G_h \le \text{max\_grid\_kwh}_h \quad (\text{if max\_grid\_window active})$$
7. **End-of-Day Neutrality**:
   $$E_{23} = \text{initial\_energy}$$

### Output Actions:
- If $C_h > 10^{-5}$: `battery_action = "charge"`, `battery_kwh = round(C_h, 4)`
- Else if $D_h > 10^{-5}$: `battery_action = "discharge"`, `battery_kwh = round(D_h, 4)`
- Else: `battery_action = "idle"`, `battery_kwh = 0.0`

---

## 05 — Replay Validator

Before emitting the HTTP response, an independent verification function audits the generated plan:
1. Hourly energy balance holds: $|G_h + S_h + D_h - (\text{demand}_h + C_h)| \le 0.01$.
2. $S_h \le \text{effective\_solar}_h + 0.01$.
3. Battery transitions and rate bounds hold every hour.
4. $E_{23} == \text{initial\_energy} \pm 0.01$.
5. Recalculated metrics:
   - $\text{total\_grid\_kwh} = \sum G_h$
   - $\text{total\_cost\_bdt} = \sum (G_h \cdot \text{tariff}_h)$
   - $\text{peak\_grid\_kwh} = \max_h G_h$
   Match the plan within official tolerance.

---

## 06 — Project Structure

```
BUP_CSE_Fest_Hackathon/
├── manage.py
├── core/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── energy/
│   ├── apps.py
│   ├── urls.py                 # GET /health, POST /optimize-energy
│   ├── views.py                # Thin APIViews orchestrating the pipeline
│   ├── serializers.py          # Strict DRF input/output schemas
│   ├── exceptions.py           # Controlled 500s without stack traces
│   ├── tests.py                # Automated test runner with the 10 sample cases
│   └── services/
│       ├── __init__.py
│       ├── llm_interpreter.py  # OpenAI tool-calling + heuristic fallback
│       ├── guardrail.py        # Deterministic directive validation
│       ├── optimizer.py        # OR-Tools GLOP LP optimizer
│       └── replay_validator.py  # Replay validator for physical constraints
├── requirement.txt
└── README.md
```

---

*BUP CSE FEST 2026 — Smart Campus Energy Optimization Challenge*
