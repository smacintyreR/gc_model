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
                p_set=solar["Generation"], carrier="solar")

    # Add battery
    energy_capacity_kwh = 500
    power_capacity_kw = 250

    # Add storage unit (state of charge)
    n.add("StorageUnit",
        name="battery",
        bus="office",
        p_set=0.0,
        p_nom=power_capacity_kw,
        max_hours=energy_capacity_kwh / power_capacity_kw,
        efficiency_store=0.95,
        efficiency_dispatch=0.95,
        cyclic_state_of_charge=False,
        capital_cost=0.0,  # optional if not modeling economics yet
    )

    # Add grid connection
    network.add("Link", "grid_import", bus0="grid", bus1="office",  # FIX: Ensure correct bus names
                p_nom_extendable=True, marginal_cost=market["ImportWholesalePrice"])

    network.add("Link", "grid_export", bus0="office", bus1="grid",
                p_nom_extendable=True, marginal_cost=-market["ExportWholesalePrice"])
    
    print(network)

    return network
