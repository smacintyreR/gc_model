def optimize_battery(network):
    """Solves the optimization problem to minimize energy costs."""
    # Define objective: minimize energy costs & demand charges
    network.optimize(network.snapshots, solver_name="cbc", formulation="kirchhoff")