from data_loader import load_data
from optimizer import build_linopy_model
from network_setup import setup_linopy_network
from results import plot_results, summarize_returns, cost_comparison
from model_validation import validate_model

def main():
    # Load input data
    load, solar, market = load_data("data/load_data.csv", "data/solar_data.csv", "data/market_data.csv")

    # Build linopy model and solve battery optimization
    results,  model = build_linopy_model(load=load,solar=solar,import_price=market['ImportWholesalePrice'],
                     export_price=market['ExportWholesalePrice'], timestamps=load.index)

    # Generate results & analysis
    timestamps = model.variables.coords["t"]

    # Save plots and produce results
    plot_results(results, timestamps, load, solar)

    # Calculate and plot expected results
    summarize_returns(results, market['ImportWholesalePrice'], market['ExportWholesalePrice'], timestamps)

    # Perform cost comparison between base case and battery/solar case
    cost_comparison(results, timestamps, load,market['ImportWholesalePrice'], market['ExportWholesalePrice'],  solar)

    # Perform some common sense model validation
    validate_model(results, timestamps)


if __name__ == "__main__":
    main()