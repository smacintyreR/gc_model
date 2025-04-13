import matplotlib.pyplot as plt
import pandas as pd
import os

def plot_results(results, timestamps, load, solar, output_dir="results"):
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
    net_load = load['ImportkWh'] - solar["Generation"]
    print(net_load)

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
    plt.plot(net_load.index, net_load, label="Net Load (Load - Solar)", color="brown")
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



def summarize_returns(results, import_price, export_price, timestamps, output_dir="results"):
    """
    Summarize monthly returns from import, export, and net revenue.
    
    Parameters:
        results (xr.Dataset): xarray Dataset with ['import_grid', 'export_grid']
        import_price (pd.Series): Import price (indexed by timestamp)
        export_price (pd.Series): Export price (indexed by timestamp)
        timestamps (pd.Index): DatetimeIndex
        output_dir (str): Folder to save CSV or plots
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert to Series and align
    import_grid = results.import_grid.to_series().reindex(timestamps).astype(float)
    export_grid = results.export_grid.to_series().reindex(timestamps).astype(float)
    import_price = import_price.reindex(timestamps).astype(float)
    export_price = export_price.reindex(timestamps).astype(float)

    # Compute cost/revenue per timestep
    import_cost = import_grid * import_price
    export_revenue = export_grid * export_price
    net_revenue = export_revenue - import_cost

    # Group by month
    df = pd.DataFrame({
        "import_cost": import_cost,
        "export_revenue": export_revenue,
        "net_revenue": net_revenue
    })
    df["month"] = timestamps.to_series().dt.to_period("M").values

    monthly_summary = df.groupby("month").sum()

    # Save to CSV
    monthly_summary.to_csv(os.path.join(output_dir, "monthly_returns.csv"))

    # Plot
    monthly_summary.plot(kind="bar", stacked=True, figsize=(12, 6), color=["crimson", "seagreen", "grey"])
    plt.title("Monthly Economic Returns")
    plt.ylabel("AUD")
    plt.xlabel("Month")
    plt.grid(True, axis="y")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "monthly_returns.png"))
    plt.close()




def cost_comparison(results, timestamps, load,import_price, export_price, solar, output_dir="results"):
    """
    Perform cost comparison calculations based for battery + solar case vs no battery/solar.
    Produces monthly cost saving csv summary.

    Parameters:
        results (xr.Dataset): xarray Dataset with data variables ['soc', 'import_grid', 'export_grid']
        timestamps (pd.Index): Datetime index matching the model time steps
        load (pd.Series): Load data indexed by time
        solar (pd.Series): Solar production data indexed by time
        output_dir (str): Directory to save PNG plots and results csvs
    """
    timestamps = pd.to_datetime(timestamps)
    soc = results.soc.to_series().reindex(timestamps)
    import_grid = results.import_grid.to_series().reindex(timestamps)
    export_grid = results.export_grid.to_series().reindex(timestamps)
    charge = results.charge.to_series().reindex(timestamps)
    discharge = results.discharge.to_series().reindex(timestamps)
    net_flow = import_grid - export_grid

    load = load.reindex(timestamps).astype(float)
    solar = solar.reindex(timestamps).astype(float)
    import_price = import_price.reindex(timestamps).astype(float)
    net_load = load - solar

    is_weekday = timestamps.to_series().dt.weekday < 5
    months = timestamps.to_series().dt.month

    print(import_grid)
    print(import_price)
    print(load)
    print(solar)

        # === Cost Comparison Analysis ===
    df = pd.DataFrame({
        "import_grid": import_grid,
        "import_price": import_price,
        "load": load["ImportkWh"],
        "solar": solar["Generation"]
    })
    df["month"] = df.index.month
    df["is_weekday"] = df.index.weekday < 5

    # With battery and solar
    df["cost_with_battery"] = df["import_grid"] * df["import_price"]
    peak_wd = df[df["is_weekday"]].groupby("month")["import_grid"].max() * 12
    peak_we = df[~df["is_weekday"]].groupby("month")["import_grid"].max() * 3
    cost_with_battery = df.groupby("month")["cost_with_battery"].sum() + peak_wd + peak_we

    # Without battery and solar (just load)
    df["import_no_solar"] = df["load"]
    df["cost_no_solar"] = df["import_no_solar"] * df["import_price"]
    peak_wd_nosolar = df[df["is_weekday"]].groupby("month")["import_no_solar"].max() * 12
    peak_we_nosolar = df[~df["is_weekday"]].groupby("month")["import_no_solar"].max() * 3
    cost_no_solar = df.groupby("month")["cost_no_solar"].sum() + peak_wd_nosolar + peak_we_nosolar

    # Monthly savings
    monthly_savings = cost_no_solar - cost_with_battery
    summary = pd.DataFrame({
        "cost_with_battery": cost_with_battery,
        "cost_no_solar": cost_no_solar,
        "monthly_savings": monthly_savings
    })

    # Save summary to CSV
    summary.to_csv(f"{output_dir}/monthly_cost_summary.csv")


    # Plot Monthly Cost Savings
    plt.figure(figsize=(10, 5))
    monthly_savings.plot(kind="bar", color="mediumseagreen")
    plt.title("Monthly Cost Savings")
    plt.ylabel("AUD")
    plt.xlabel("Month")
    plt.grid(True, axis="y")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/monthly_savings.png")
    plt.close()


