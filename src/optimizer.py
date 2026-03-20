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
    model.add_constraints(soc.loc[T[0]] == 0, name="soc_initial")

    # State of charge constraint
    soc_t1 = soc.sel(t=T[1:])

    # We must assign the coords of the shifted variables to match the t1 variables,
    # otherwise xarray aligns them by their original time values!
    soc_t0 = soc.sel(t=T[:-1]).assign_coords(t=T[1:])
    charge_t0 = charge.sel(t=T[:-1]).assign_coords(t=T[1:])
    discharge_t0 = discharge.sel(t=T[:-1]).assign_coords(t=T[1:])

    model.add_constraints(
        (soc_t1 - soc_t0) - (eta * charge_t0 - discharge_t0 / eta) == 0,
        name="soc_balance"
    )

    # Monthly peak power weekend and weekday related constraints
    for m in M:

        # Prepare month masks for weekend and weekday
        month_mask = T.month == m
        mask_month_weekday = (month_mask & is_weekday).to_numpy() if hasattr(month_mask & is_weekday, 'to_numpy') else (month_mask & is_weekday)
        mask_month_weekend = (month_mask & ~is_weekday).to_numpy() if hasattr(month_mask & ~is_weekday, 'to_numpy') else (month_mask & ~is_weekday)

        # Retrieve the import_grid variables for month weekdays and weekends
        import_month_weekday = import_grid[mask_month_weekday]
        import_month_weekend = import_grid[mask_month_weekend]

        if len(import_month_weekday.coords["t"]) > 0:
            model.add_constraints(
                peak_wd.sel(m=m) - import_month_weekday >= 0,
                name=f"max_power_weekday_month_{m}"
            )

        if len(import_month_weekend.coords["t"]) > 0:
            model.add_constraints(
                peak_we.sel(m=m) - import_month_weekend >= 0,
                name=f"max_power_weekend_month_{m}"
            )
            

    # Power balance constraint - ensuring load always met
    load_solar_diff = load.iloc[:, 0].to_numpy() - solar.iloc[:, 0].to_numpy()
    model.add_constraints(
        (import_grid - export_grid) + (discharge - charge) == load_solar_diff,
        name="power_balance"
    )

    model.add_constraints(
        export_grid - discharge <= solar.iloc[:, 0].to_numpy(),
        name="export_constraint"
    )

    model.add_constraints(
        discharge - soc <= 0,
        name="discharge_constraint"
    )

    # Define max power charge/discharge in 30m timestep
    M_power = battery_power_kw * eta * vars["dt_hours"]

    # Attempts to replicate charge/discharge exlusion while maintaining linearity
    model.add_constraints(
        discharge + charge <= M_power,
        name="charge_discharge_exclusion"
    )

    # Binary constraints for charge/discharge exclusion - NOT IN USE
    # model.add_constraints(charge - M_power * is_charging <= 0, name="charge_binary_link")
    # model.add_constraints(discharge - M_power * is_discharging <= 0, name="discharge_binary_link")
    # model.add_constraints(is_charging + is_discharging <= 1, name="no_simultaneous")


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