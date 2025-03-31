import matplotlib.pyplot as plt

def generate_results(network):
    """Extracts and plots key results."""
    battery_soc = network.stores_t.e["battery"]
    imports = network.links_t.p1["grid_import"]
    exports = network.links_t.p0["grid_export"]

    plt.figure(figsize=(12, 5))
    plt.plot(battery_soc, label="Battery State of Charge (kWh)")
    plt.plot(imports, label="Grid Imports (kW)", linestyle="dashed")
    plt.plot(exports, label="Grid Exports (kW)", linestyle="dotted")
    plt.legend()
    plt.title("Battery Operation & Grid Interaction")
    plt.show()