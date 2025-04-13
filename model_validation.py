import pandas as pd
import matplotlib.pyplot as plt
import os


def validate_model(results, timestamps, load, solar, battery_capacity_kwh=500, output_dir="validation"):
    """
    Perform validation checks on the optimization results.

    Parameters:
        results (xr.Dataset): Optimization results
        timestamps (pd.Index): Time index for results
        load (pd.Series): Load profile
        solar (pd.Series): Solar profile
        battery_capacity_kwh (float): Maximum battery capacity
        output_dir (str): Directory to save validation plots
    """
    os.makedirs(output_dir, exist_ok=True)

    timestamps = pd.to_datetime(timestamps)
    soc = results.soc.to_series().reindex(timestamps)
    charge = results.charge.to_series().reindex(timestamps)
    discharge = results.discharge.to_series().reindex(timestamps)

    # === Check 1: SoC Bounds ===
    violations = (soc < 0) | (soc > battery_capacity_kwh)
    if violations.any():
        print("[Warning] State of charge exceeds bounds at:")
        print(soc[violations])

    # === Check 2: Discharge only when SoC > 0 ===
    empty_and_discharging = (soc <= 0.01) & (discharge > 0.01)
    if empty_and_discharging.any():
        print("[Warning] Battery discharges when empty at:")
        print(discharge[empty_and_discharging])

    # === Check 3: No simultaneous charge and discharge ===
    simultaneous = (charge > 0.01) & (discharge > 0.01)
    if simultaneous.any():
        print("[Warning] Simultaneous charging and discharging at:")
        print(pd.DataFrame({"charge": charge[simultaneous], "discharge": discharge[simultaneous]}))

    # === Check 4: Plot suspect periods ===
    sample_range = timestamps[:96]  # First two days
    plt.figure(figsize=(14, 5))
    soc.loc[sample_range].plot(label="State of Charge", color="orange")
    charge.loc[sample_range].plot(label="Charge", color="green")
    discharge.loc[sample_range].plot(label="Discharge", color="red")
    plt.title("Battery SoC, Charge and Discharge (First 2 Days)")
    plt.ylabel("kWh")
    plt.xlabel("Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/battery_check_plot.png")
    plt.close()

    print("Validation complete. Warnings shown above if any violations occurred.")
