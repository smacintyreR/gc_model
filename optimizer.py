import pandas as pd
from network_setup import setup_linopy_network

def build_linopy_model(load, solar, import_price, export_price, timestamps, battery_capacity_kwh=500, battery_power_kw=250):
    # === Set up model and variables from network_setup.py ===
    model, vars = setup_linopy_network(
        timestamps,
        battery_capacity_kwh=battery_capacity_kwh,
        battery_power_kw=battery_power_kw
    )

    # Unpack variables
    import_grid = vars["import_grid"]
    export_grid = vars["export_grid"]
    charge = vars["charge"]
    discharge = vars["discharge"]
    soc = vars["soc"]
    T = vars["T"]
    M = vars["M"]
    is_weekday = vars["is_weekday"]
    month_map = vars["month_map"]
    eta = vars["battery_efficiency"]
    peak_wd = vars["peak_wd"]
    peak_we = vars["peak_we"]

    # === Constraints ===

    # Initial SoC
    model.add_constraints(soc[T[0]] == 0, name="soc_initial")

    #print(model)

    for t1 in T[1:]:  # Starting from second time step
        t0 = T[T.get_loc(t1) - 1]  # Get the previous time step
        soc_update_expr = soc[t0] + eta * charge[t0] - discharge[t0] / eta
        model.add_constraints(
            soc[t1] - soc_update_expr == 0,
            name=f"soc_balance_{t1}"
        )


    # Power balance constraint



    for t in T:

        #print(solar.loc[t][0])
        #print(load.loc[t][0])
        model.add_constraints(
        (import_grid[t] - export_grid[t]) + (discharge[t] - charge[t]) == (load.loc[t][0] - solar.loc[t][0]),
            name=f"power_balance_{t}"
        )


        model.add_constraints(
            export_grid[t] - discharge[t] <= solar.loc[t][0],
            name=f"export_constraint_{t}"
        )

        model.add_constraints(discharge[t] - soc[t] <= 0, name=f"discharge_limit_{t}")




    # === Objective function ===
    objective = (
        (import_grid * import_price).sum()
        - (export_grid * export_price).sum()
    )

    model.add_objective(objective, sense="min")

    print(model)
    print(model.objective)

    model.solve(solver_name="highs")

    results = model.variables.solution
    return results, model