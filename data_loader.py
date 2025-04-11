import pandas as pd

def load_data(load_path, solar_path, market_path):
    """Loads and processes input CSV files, aligning timestamps to 2024 with leap year handling."""

    # Load datasets
    load = pd.read_csv(load_path, parse_dates=["Datetime"], index_col="Datetime")
    solar = pd.read_csv(solar_path, parse_dates=["Datetime"], index_col="Datetime")
    market = pd.read_csv(market_path, parse_dates=["Datetime"], index_col="Datetime")

    market["ImportWholesalePrice"] /= 1000
    market["ExportWholesalePrice"] /= 1000

    # Define 2024 30m index without feb 29
    full_index = pd.date_range(start="2024-01-01 00:00:00", end="2024-12-31 23:30:00", freq="30T")
    # Remove all timestamps where the date is February 29
    clean_index = full_index[~((full_index.month == 2) & (full_index.day == 29))]

    # Treat load first
    # Timezone is Australia/Melbourne
    df_load = load.tz_localize("Australia/Melbourne", ambiguous=True)

    # Convert to GMT+10 timezone
    df_load = df_load.tz_convert('Etc/GMT-10')

    # Shift first 2 entries
    df_load_reordered = pd.concat([df_load.iloc[2:], df_load.iloc[:2]])

    # Set index to 2024 index
    df_load_reordered.index = clean_index


    # Treat market data
    df_market_resampled = market.resample('30min').mean()

    # Remove february 29
    df_market_resampled = df_market_resampled[~((df_market_resampled.index.month == 2) & (df_market_resampled.index.day == 29))]

    # Treat solar data
    solar.index = clean_index






    df_load_reordered.to_csv("processed_load.csv")
    solar.to_csv("processed_solar.csv")
    df_market_resampled.to_csv("processed_market.csv")

    # Take first 5 timesteps
    # df_load_reordered = df_load_reordered[:400]
    # solar = solar[:400]
    # df_market_resampled = df_market_resampled[:400]

    return df_load_reordered, solar, df_market_resampled



