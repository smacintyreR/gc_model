from data_loader import load_data
from optimizer import build_linopy_model
from network_setup import setup_linopy_network
from results import plot_results, summarize_returns, cost_comparison

def main():
    # Load input data
    load, solar, market = load_data("data/load_data.csv", "data/solar_data.csv", "data/market_data.csv")

    # Set up PyPSA network

    # Optimize battery storage
    results,  model = build_linopy_model(load=load,solar=solar,import_price=market['ImportWholesalePrice'],
                     export_price=market['ExportWholesalePrice'], timestamps=load.index)

    # Generate results & analysis
    timestamps = model.variables.coords["t"]

# Save plots
    plot_results(results, timestamps, load, solar)

    summarize_returns(results, market['ImportWholesalePrice'], market['ExportWholesalePrice'], timestamps)

    cost_comparison(results, timestamps, load, solar)


if __name__ == "__main__":
    main()