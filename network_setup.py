import pypsa

def setup_network(load, solar, market):
    """Sets up the PyPSA network with grid, solar, and battery components."""
    network = pypsa.Network()

    # Ensure market data is aligned with load index
    market = market.reindex(load.index, method="ffill")

    # Check for duplicate timestamps
    if not load.index.is_monotonic_increasing:
        load = load.sort_index()

    # Add time steps
    network.set_snapshots(load.index)

    # Add buses
    network.add("Bus", "office")
    network.add("Bus", "grid")  # FIX: Define 'grid' bus

    # Add load
    network.add("Load", "building_load", bus="office", p_set=load["ImportkWh"])

    # Add solar
    network.add("Generator", "solar_PV", bus="office",
                p_max_pu=solar["Generation"], carrier="solar", p_nom=1)

    # Add battery
    network.add("Store", "battery", bus="office", e_nom=500, p_nom=250, e_cyclic=True)

    # Add grid connection
    network.add("Link", "grid_import", bus0="grid", bus1="office",  # FIX: Ensure correct bus names
                p_nom_extendable=True, marginal_cost=market["ImportWholesalePrice"])

    network.add("Link", "grid_export", bus0="office", bus1="grid",
                p_nom_extendable=True, marginal_cost=-market["ExportWholesalePrice"])

    return network
