import linopy
import pandas as pd
import numpy as np

def setup_linopy_network(timestamps, battery_capacity_kwh=500, battery_power_kw=250, battery_efficiency=0.95):
    dt_hours = 0.5
    model = linopy.Model()

    # Time indices
    T = pd.Index(timestamps, name="t")
    months = timestamps.to_series().dt.month.unique()
    M = pd.Index(months, name="m")

    # Time-based masks and mappings
    is_weekday = timestamps.to_series().dt.weekday < 5
    month_map = timestamps.to_series().dt.month

    # === Variables ===
    import_grid = model.add_variables(lower=0, name="import_grid", coords=[T])
    export_grid = model.add_variables(lower=0, name="export_grid", coords=[T])
    charge = model.add_variables(lower=0, upper=battery_power_kw * dt_hours, name="charge", coords=[T])
    discharge = model.add_variables(lower=0, upper=battery_power_kw * dt_hours, name="discharge", coords=[T])
    soc = model.add_variables(lower=0, upper=battery_capacity_kwh, name="soc", coords=[T])
    peak_wd = model.add_variables(lower=0, name="peak_import_weekday", coords=[M])
    peak_we = model.add_variables(lower=0, name="peak_import_weekend", coords=[M])

    # Add binary variables
    is_charging = model.add_variables(binary=True, name="is_charging", coords=[T])
    is_discharging = model.add_variables(binary=True, name="is_discharging", coords=[T])

    # === Package variables for reuse ===
    variables = {
        "import_grid": import_grid,
        "export_grid": export_grid,
        "charge": charge,
        "discharge": discharge,
        "soc": soc,
        "peak_wd": peak_wd,
        "peak_we": peak_we,
        "T": T,
        "M": M,
        "is_weekday": is_weekday,
        "month_map": month_map,
        "battery_efficiency": battery_efficiency,
        "dt_hours": dt_hours,
        "is_charging": is_charging,
        "is_discharging": is_discharging
    }

    return model, variables