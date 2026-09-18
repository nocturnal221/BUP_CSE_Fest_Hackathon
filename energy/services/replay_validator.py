"""Replay Validator to independently audit physical and operational schedule constraints."""
from typing import List, Dict, Any


def replay_validate_schedule(
    hourly_plan: List[Dict[str, Any]],
    hours_data: List[Dict[str, Any]],
    battery_data: Dict[str, Any],
    directives: List[Dict[str, Any]],
    tolerance: float = 0.05
) -> Dict[str, Any]:
    """
    Replays the schedule step-by-step and validates:
    1. Hourly energy balance
    2. Solar availability limits
    3. Battery transitions, bounds, and rate limits
    4. End-of-day battery neutrality
    5. Directives compliance
    Returns recalculated totals and confirmation status.
    """
    if len(hourly_plan) != 24:
        raise ValueError(f"Expected 24 plan hours, got {len(hourly_plan)}")

    cap = float(battery_data['capacity_kwh'])
    init_energy = float(battery_data['initial_energy_kwh'])
    base_min = float(battery_data['minimum_energy_kwh'])
    max_charge = float(battery_data['max_charge_kwh_per_hour'])
    max_discharge = float(battery_data['max_discharge_kwh_per_hour'])

    effective_solar = [float(h['solar_kwh']) for h in hours_data]
    min_energy = [base_min] * 24
    max_charge_limit = [max_charge] * 24
    max_discharge_limit = [max_discharge] * 24
    max_grid_limit = [float('inf')] * 24

    for d in directives:
        if not d.get('applies'):
            continue
        dtype = d.get('directive_type')
        adj = d.get('structured_adjustment') or {}
        hours = adj.get('hours', [])

        if dtype == 'solar_reduction':
            factor = float(adj.get('factor', 1.0))
            for h in hours:
                if 0 <= h < 24:
                    effective_solar[h] = min(effective_solar[h], float(hours_data[h]['solar_kwh']) * factor)
        elif dtype == 'minimum_battery_reserve':
            res = float(adj.get('minimum_energy_kwh', 0.0))
            for h in hours:
                if 0 <= h < 24:
                    min_energy[h] = max(min_energy[h], res)
        elif dtype == 'no_charge_window':
            for h in hours:
                if 0 <= h < 24:
                    max_charge_limit[h] = 0.0
        elif dtype == 'no_discharge_window':
            for h in hours:
                if 0 <= h < 24:
                    max_discharge_limit[h] = 0.0
        elif dtype == 'max_grid_window':
            mg = float(adj.get('max_grid_kwh', float('inf')))
            for h in hours:
                if 0 <= h < 24:
                    max_grid_limit[h] = min(max_grid_limit[h], mg)

    prev_energy = init_energy
    recalc_total_grid = 0.0
    recalc_total_cost = 0.0
    peak_grid = 0.0

    for h, step in enumerate(hourly_plan):
        g = float(step['grid_kwh'])
        s = float(step['solar_used_kwh'])
        action = step['battery_action']
        b_kwh = float(step['battery_kwh'])
        e_after = float(step['battery_energy_after_kwh'])
        demand = float(hours_data[h]['demand_kwh'])
        tariff = float(hours_data[h]['tariff_bdt_per_kwh'])

        recalc_total_grid += g
        recalc_total_cost += g * tariff
        if g > peak_grid:
            peak_grid = g

        # 1. Solar limit check
        if s > effective_solar[h] + tolerance:
            raise ValueError(f"Hour {h}: Solar used ({s}) exceeds effective solar ({effective_solar[h]})")

        # 2. Grid limit check
        if g > max_grid_limit[h] + tolerance:
            raise ValueError(f"Hour {h}: Grid import ({g}) exceeds max grid cap ({max_grid_limit[h]})")

        # 3. Action and battery limits
        c_val = b_kwh if action == 'charge' else 0.0
        d_val = b_kwh if action == 'discharge' else 0.0

        if c_val > max_charge_limit[h] + tolerance:
            raise ValueError(f"Hour {h}: Charge ({c_val}) exceeds limit ({max_charge_limit[h]})")
        if d_val > max_discharge_limit[h] + tolerance:
            raise ValueError(f"Hour {h}: Discharge ({d_val}) exceeds limit ({max_discharge_limit[h]})")

        # 4. Energy balance check
        # Balance: g + s + d_val = demand + c_val
        diff = (g + s + d_val) - (demand + c_val)
        if abs(diff) > tolerance:
            raise ValueError(f"Hour {h}: Energy balance violated. Generation {g + s + d_val} vs Demand+Charge {demand + c_val}")

        # 5. Battery transition check
        expected_e = prev_energy + c_val - d_val
        if abs(e_after - expected_e) > tolerance:
            raise ValueError(f"Hour {h}: Battery transition mismatch. Expected {expected_e}, got {e_after}")

        if e_after < min_energy[h] - tolerance or e_after > cap + tolerance:
            raise ValueError(f"Hour {h}: Battery energy {e_after} outside allowed range [{min_energy[h]}, {cap}]")

        prev_energy = e_after

    # 6. End of day neutrality check
    if abs(prev_energy - init_energy) > tolerance:
        raise ValueError(f"End-of-day neutrality violated. Final energy {prev_energy} != Initial energy {init_energy}")

    return {
        "valid": True,
        "recalculated_total_grid_kwh": round(recalc_total_grid, 2),
        "recalculated_total_cost_bdt": round(recalc_total_cost, 2),
        "recalculated_peak_grid_kwh": round(peak_grid, 2)
    }
