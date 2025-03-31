
def load_data(load_path, solar_path, market_path):
    """Loads and processes the input CSV files."""
    load = pd.read_csv(load_path, parse_dates=["Datetime"], index_col="Datetime")
    solar = pd.read_csv(solar_path, parse_dates=["Datetime"], index_col="Datetime")
    market = pd.read_csv(market_path, parse_dates=["Datetime"], index_col="Datetime")

    # Convert prices from $/MWh to $/kWh
    market["ImportWholesalePrice"] /= 1000
    market["ExportWholesalePrice"] /= 1000

    return load, solar, market