"""Linear Programming Optimizer for Campus Microgrid using Google OR-Tools GLOP."""
from typing import List, Dict, Any
from ortools.linear_solver import pywraplp


def optimize_schedule(
    hours_data: List[Dict[str, Any]],
    battery_data: Dict[str, Any],
    directives: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Formulates and solves the 24-hour cost minimization LP subject to microgrid constraints.
    """
    solver = pywraplp.Solver.CreateSolver('GLOP')
    if not solver:
        raise RuntimeError("OR-Tools GLOP solver could not be initialized.")

    infinity = solver.infinity()

    # Pre-process hourly baseline parameters
    effective_solar = [float(h['solar_kwh']) for h in hours_data]
    demand = [float(h['demand_kwh']) for h in hours_data]
    tariff = [float(h['tariff_bdt_per_kwh']) for h in hours_data]

    cap = float(battery_data['capacity_kwh'])
    init_energy = float(battery_data['initial_energy_kwh'])
    base_min = float(battery_data['minimum_energy_kwh'])
    base_max_charge = float(battery_data['max_charge_kwh_per_hour'])
    base_max_discharge = float(battery_data['max_discharge_kwh_per_hour'])

    min_energy = [base_min] * 24
    max_charge = [base_max_charge] * 24
    max_discharge = [base_max_discharge] * 24
    max_grid = [infinity] * 24

    # Apply directives
    applied_descriptions = []
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
            applied_descriptions.append(f"reduced solar to {factor*100:.0f}% for hours {hours}")

        elif dtype == 'minimum_battery_reserve':
            reserve = float(adj.get('minimum_energy_kwh', 0.0))
            for h in hours:
                if 0 <= h < 24:
                    min_energy[h] = max(min_energy[h], reserve)
            applied_descriptions.append(f"raised reserve to {reserve} kWh for hours {hours}")

        elif dtype == 'no_charge_window':
            for h in hours:
                if 0 <= h < 24:
                    max_charge[h] = 0.0
            applied_descriptions.append(f"disabled charging for hours {hours}")

        elif dtype == 'no_discharge_window':
            for h in hours:
                if 0 <= h < 24:
                    max_discharge[h] = 0.0
            applied_descriptions.append(f"disabled discharging for hours {hours}")

        elif dtype == 'max_grid_window':
            grid_cap = float(adj.get('max_grid_kwh', infinity))
            for h in hours:
                if 0 <= h < 24:
                    max_grid[h] = min(max_grid[h], grid_cap)
            applied_descriptions.append(f"capped grid import at {grid_cap} kWh for hours {hours}")

    # Create LP Variables
    G = []  # Grid draw
    S = []  # Solar used
    C = []  # Charge
    D = []  # Discharge
    E = []  # Battery energy after hour h

    for h in range(24):
        G.append(solver.NumVar(0.0, max_grid[h], f"grid_{h}"))
        S.append(solver.NumVar(0.0, max(0.0, effective_solar[h]), f"solar_{h}"))
        C.append(solver.NumVar(0.0, max_charge[h], f"charge_{h}"))
        D.append(solver.NumVar(0.0, max_discharge[h], f"discharge_{h}"))
        E.append(solver.NumVar(min_energy[h], cap, f"energy_{h}"))

    # Constraints
    for h in range(24):
        # 1. Campus Energy Balance: G[h] + S[h] + D[h] - C[h] == demand[h]
        balance = solver.Constraint(demand[h], demand[h], f"balance_{h}")
        balance.SetCoefficient(G[h], 1.0)
        balance.SetCoefficient(S[h], 1.0)
        balance.SetCoefficient(D[h], 1.0)
        balance.SetCoefficient(C[h], -1.0)

        # 2. Battery State Transition
        if h == 0:
            # E[0] - C[0] + D[0] == init_energy
            trans = solver.Constraint(init_energy, init_energy, "trans_0")
            trans.SetCoefficient(E[0], 1.0)
            trans.SetCoefficient(C[0], -1.0)
            trans.SetCoefficient(D[0], 1.0)
        else:
            # E[h] - E[h-1] - C[h] + D[h] == 0
            trans = solver.Constraint(0.0, 0.0, f"trans_{h}")
            trans.SetCoefficient(E[h], 1.0)
            trans.SetCoefficient(E[h - 1], -1.0)
            trans.SetCoefficient(C[h], -1.0)
            trans.SetCoefficient(D[h], 1.0)

    # 3. End of day neutrality: E[23] == init_energy
    neutrality = solver.Constraint(init_energy, init_energy, "neutrality_23")
    neutrality.SetCoefficient(E[23], 1.0)

    # Objective: Minimize total cost sum(G[h] * tariff[h])
    # Add tiny penalty for C and D to prevent simultaneous charge and discharge
    # Add tiny reward for solar use so solar is preferred
    objective = solver.Objective()
    for h in range(24):
        objective.SetCoefficient(G[h], tariff[h])
        objective.SetCoefficient(C[h], 1e-5)
        objective.SetCoefficient(D[h], 1e-5)
        objective.SetCoefficient(S[h], -1e-7)
    objective.SetMinimization()

    status = solver.Solve()
    if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        raise ValueError("Linear program is infeasible under the requested directives and constraints.")

    # Extract results
    hourly_plan = []
    for h in range(24):
        g_val = round(G[h].solution_value(), 4)
        s_val = round(S[h].solution_value(), 4)
        c_val = G[h].solution_value()  # placeholder, real below
        c_raw = C[h].solution_value()
        d_raw = D[h].solution_value()
        e_val = round(E[h].solution_value(), 4)

        net_b = c_raw - d_raw
        if net_b > 1e-4:
            action = "charge"
            battery_kwh = round(net_b, 4)
        elif net_b < -1e-4:
            action = "discharge"
            battery_kwh = round(-net_b, 4)
        else:
            action = "idle"
            battery_kwh = 0.0

        hourly_plan.append({
            "hour": h,
            "grid_kwh": g_val,
            "solar_used_kwh": s_val,
            "battery_action": action,
            "battery_kwh": battery_kwh,
            "battery_energy_after_kwh": e_val
        })

    total_grid = round(sum(item['grid_kwh'] for item in hourly_plan), 2)
    total_cost = round(sum(item['grid_kwh'] * tariff[h] for h, item in enumerate(hourly_plan)), 2)
    peak_grid = round(max(item['grid_kwh'] for item in hourly_plan), 2)

    if applied_descriptions:
        plan_summary = f"Optimal schedule applied: {'; '.join(applied_descriptions)}, maintaining battery neutrality and minimizing peak tariffs."
    else:
        plan_summary = "Optimal unconstrained baseline schedule shifting battery energy to avoid peak tariffs and maintaining end-of-day battery neutrality."

    return {
        "hourly_plan": hourly_plan,
        "total_grid_kwh": total_grid,
        "total_cost_bdt": total_cost,
        "peak_grid_kwh": peak_grid,
        "plan_summary": plan_summary
    }
