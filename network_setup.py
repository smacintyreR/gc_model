import pypsa

def setup_network(load, solar, market):
    """Sets up the PyPSA network with grid, solar, and battery components."""
    network = pypsa.Network()

    # Add time steps
    network.set_snapshots(load.index)

    # Add bus
    network.add("Bus", "office")

    # Add load
    network.add("Load", "building_load", bus="office", p_set=load["ImportkWh"])

    # Add solar
    network.add("Generator", "solar_PV", bus="office",
                p_max_pu=solar["Generation"], carrier="solar", p_nom=1)

    # Add battery
    network.add("Store", "battery", bus="office", e_nom=500, p_nom=250, e_cyclic=True)

    # Add grid connection
    network.add("Link", "grid_import", bus0="office", bus1="grid",
                p_nom_extendable=True, marginal_cost=market["ImportWholesalePrice"])

    network.add("Link", "grid_export", bus0="office", bus1="grid",
                p_nom_extendable=True, marginal_cost=-market["ExportWholesalePrice"])

    return network