from data_loader import load_data
from network_setup import setup_network
from optimizer import optimize_battery
from results import generate_results

def main():
    # Load input data
    load, solar, market = load_data("data/load_data.csv", "data/solar_data.csv", "data/market_data.csv")

    # Set up PyPSA network
    network = setup_network(load, solar, market)

    # Optimize battery storage
    optimize_battery(network)

    # Generate results & analysis
    generate_results(network)

if __name__ == "__main__":
    main()