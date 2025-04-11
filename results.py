import matplotlib.pyplot as plt
import pandas as pd
import os

def plot_results(results, timestamps, load, solar, output_dir="plots"):
    """
    Plot state of charge, import, export, solar, load, and net grid power over time.
    Save each plot as a PNG file.

    Parameters:
        results (xr.Dataset): xarray Dataset with data variables ['soc', 'import_grid', 'export_grid']
        timestamps (pd.Index): Datetime index matching the model time steps
        load (pd.Series): Load data indexed by time
        solar (pd.Series): Solar production data indexed by time
        output_dir (str): Directory to save PNG plots
    """
    os.makedirs(output_dir, exist_ok=True)

    # Ensure timestamps is a DatetimeIndex
    timestamps = pd.to_datetime(timestamps)

    # Convert xarray DataArrays to pandas Series
    soc = results.soc.to_series().reindex(timestamps)
    import_grid = results.import_grid.to_series().reindex(timestamps)
    export_grid = results.export_grid.to_series().reindex(timestamps)
    charge = results.charge.to_series().reindex(timestamps)
    discharge = results.discharge.to_series().reindex(timestamps)
    net_flow = import_grid - export_grid

    # Reindex load and solar
    load = load.reindex(timestamps).astype(float)
    solar = solar.reindex(timestamps).astype(float)
    net_load = load - solar

    # === Plot State of Charge ===
    plt.figure(figsize=(14, 4))
    soc.plot(label="State of Charge (kWh)", color="darkorange")
    plt.title("Battery State of Charge")
    plt.ylabel("kWh")
    plt.xlabel("Time")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/soc.png")
    plt.close()

    # === Plot Grid Import and Export ===
    plt.figure(figsize=(14, 4))
    import_grid.plot(label="Import from Grid (kWh)", color="steelblue")
    export_grid.plot(label="Export to Grid (kWh)", color="seagreen")
    plt.title("Grid Power Flows")
    plt.ylabel("kWh per timestep")
    plt.xlabel("Time")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/import_export.png")
    plt.close()

    # === Plot Net Grid Flow ===
    plt.figure(figsize=(14, 4))
    net_flow.plot(label="Net Grid Flow (+ve = import, -ve = export)", color="purple")
    plt.axhline(0, color="black", linestyle="--")
    plt.title("Net Grid Flow")
    plt.ylabel("kWh per timestep")
    plt.xlabel("Time")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/net_grid_flow.png")
    plt.close()

    # === Plot Load and Solar Production ===
    plt.figure(figsize=(14, 4))
    plt.plot(timestamps, load, label="Load (kWh)", color="red")
    plt.plot(timestamps, solar, label="Solar Production (kWh)", color="gold")
    plt.title("Load and Solar Production")
    plt.ylabel("kWh per timestep")
    plt.xlabel("Time")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/load_solar.png")
    plt.close()

    # === Plot Net Load (Load - Solar) ===
    plt.figure(figsize=(14, 4))
    net_load.plot(label="Net Load (Load - Solar)", color="brown")
    plt.axhline(0, color="black", linestyle="--")
    plt.title("Net Load")
    plt.ylabel("kWh per timestep")
    plt.xlabel("Time")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/net_load.png")
    plt.close()

    # === Plot Battery Charge and Discharge ===
    plt.figure(figsize=(14, 4))
    charge.plot(label="Battery Charge (kWh)", color="green")
    discharge.plot(label="Battery Discharge (kWh)", color="orange")
    plt.title("Battery Charge and Discharge")
    plt.ylabel("kWh per timestep")
    plt.xlabel("Time")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/charge_discharge.png")
    plt.close()

