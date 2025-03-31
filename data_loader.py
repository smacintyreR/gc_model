import pandas as pd

def load_data(load_path, solar_path, market_path):
    """Loads and processes input CSV files, aligning timestamps to 2024 with leap year handling."""

    # Load datasets
    load = pd.read_csv(load_path, parse_dates=["Datetime"], index_col="Datetime")
    solar = pd.read_csv(solar_path, parse_dates=["Datetime"], index_col="Datetime")
    market = pd.read_csv(market_path, parse_dates=["Datetime"], index_col="Datetime")

    # Load data: Assume it's in 'Australia/Melbourne' but naive
    if load.index.tzinfo is None:
        load = load.tz_localize("Australia/Melbourne", ambiguous="NaT", nonexistent="shift_forward")
    else:
        load = load.tz_convert("Australia/Melbourne")

    # Solar data: Already timezone-aware (GMT+10), convert to 'Australia/Melbourne'
    solar = solar.tz_convert("Australia/Melbourne")

    # Market data: Naive but should be GMT+10 → Convert to 'Australia/Melbourne'
    if market.index.tzinfo is None:
        market = market.tz_localize("Etc/GMT-10").tz_convert("Australia/Melbourne")
    else:
        market = market.tz_convert("Australia/Melbourne")

    # Convert wholesale prices from $/MWh to $/kWh
    market["ImportWholesalePrice"] /= 1000
    market["ExportWholesalePrice"] /= 1000

    # Resample market data (5-minute → 30-minute intervals)
    market_resampled = market.resample("30T").mean()

    # Define full 2024 time range in 'Australia/Melbourne'
    full_index = pd.date_range(start="2024-01-01", end="2024-12-31 23:30", freq="30T", tz="Australia/Melbourne")

    # Resample solar and load data to 30-minute intervals
    load_resampled = load.resample("30T").mean()
    solar_resampled = solar.resample("30T").mean()

    # Reindex all datasets to ensure full 2024 coverage
    load_resampled = load_resampled.reindex(full_index, method="ffill")
    solar_resampled = solar_resampled.reindex(full_index, method="ffill")
    market_resampled = market_resampled.reindex(full_index, method="ffill")

    # Handle leap year by copying February 29 values from February 28
    feb_29_index = pd.date_range("2024-02-29", periods=1, freq="30T", tz="Australia/Melbourne")
    load_resampled.loc[feb_29_index] = load_resampled.loc["2024-02-28"]
    solar_resampled.loc[feb_29_index] = solar_resampled.loc["2024-02-28"]
    market_resampled.loc[feb_29_index] = market_resampled.loc["2024-02-28"]

    # Convert all timestamps to naive (remove timezone)
    load_resampled = load_resampled.tz_convert(None)
    solar_resampled = solar_resampled.tz_convert(None)
    market_resampled = market_resampled.tz_convert(None)

    return load_resampled, solar_resampled, market_resampled



