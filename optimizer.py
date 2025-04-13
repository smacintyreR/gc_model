import pandas as pd
from network_setup import setup_linopy_network

def build_linopy_model(load, solar, import_price, export_price, timestamps, battery_capacity_kwh=500, battery_power_kw=250, weekend_tariff=3,
                       weekday_tariff=12):

    # Setup linopy network
    model, vars = setup_linopy_network(
        timestamps,
        battery_capacity_kwh=battery_capacity_kwh,
        battery_power_kw=battery_power_kw
    )

    # Unpack variables from dictionary
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
    # is_charging = vars["is_charging"]
    # is_discharging = vars["is_discharging"]

    # Initialise constraints

    # Initial SoC == 0
    model.add_constraints(soc[T[0]] == 0, name="soc_initial")

    # State of charge constraint
    for t1 in T[1:]:  # Starting from second time step

        t0 = T[T.get_loc(t1) - 1]  # Get the previous time step

        model.add_constraints(
            (soc[t1] - soc[t0]) - (eta * charge[t0] - discharge[t0] / eta) == 0,
            name=f"soc_balance_{t1}"
        )

    # Monthly peak power weekend and weekday related constraints
    for m in M:

        # Prepare month masks for weekend and weekday
        month_mask = T.month == m
        mask_month_weekday = (month_mask & is_weekday).to_numpy()
        mask_month_weekend = (month_mask & ~is_weekday).to_numpy()

        # Retrieve the import_grid variables for month weekdays and weekends
        import_month_weekday = import_grid[mask_month_weekday]
        import_month_weekend = import_grid[mask_month_weekend]

        # Retrieve associated time indexes
        time_index_weekday = import_month_weekday.coords["t"].values
        time_index_weekend = import_month_weekend.coords["t"].values

        # Add constraints to define peak_wd as peak power import for month
        for t in time_index_weekday:
                    
                    model.add_constraints(
            peak_wd[m] - import_month_weekday[t] >= 0,
            name=f"max_power_weekday_{t}_month_{m}"
            )
           
        for t in time_index_weekend:
                    
                    model.add_constraints(
            peak_we[m] - import_month_weekend[t] >= 0,
            name=f"max_power_weekend_{t}_month_{m}"
            )
            

    # Power balance constraint - ensuring load always met
    for t in T:

        model.add_constraints(
        (import_grid[t] - export_grid[t]) + (discharge[t] - charge[t]) == (load.loc[t][0] - solar.loc[t][0]),
            name=f"power_balance_{t}"
        )

        model.add_constraints(
            export_grid[t] - discharge[t] <= solar.loc[t][0],
            name=f"export_constraint_{t}"
        )

        model.add_constraints(
               discharge[t] - soc[t] <= 0,
               name=f"discharge_constraint_{t}"
        )

        # Define max power charge/discharge in 30m timestep
        M_power = battery_power_kw * eta * vars["dt_hours"]

        # Attempts to replicate charge/discharge exlusion while maintaining linearity
        model.add_constraints(discharge[t] + charge[t] <= M_power, name=f"charge_discharge_exclusion_{t}")

        # Binary constraints for charge/discharge exclusion - NOT IN USE
        # model.add_constraints(charge[t] - M_power * is_charging[t] <= 0, name=f"charge_binary_link_{t}")
        # model.add_constraints(discharge[t] - M_power * is_discharging[t] <= 0, name=f"discharge_binary_link_{t}")
        # model.add_constraints(is_charging[t] + is_discharging[t] <= 1, name=f"no_simultaneous_{t}")


    # Define objective function
    objective = (
    (import_grid * (import_price.to_numpy())).sum() - (export_grid*(export_price.to_numpy())).sum() + weekend_tariff*peak_we.sum() + weekday_tariff*peak_wd.sum()
    )

    # Add objective to model
    model.add_objective(objective, sense="min")

    # Solve model
    model.solve(solver_name="highs")

    # Report results
    results = model.variables.solution

    return results, model