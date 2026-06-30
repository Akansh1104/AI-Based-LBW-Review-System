import numpy as np

def simulate_side_view(front_positions):
    """
    Generates a physics-inspired parabolic side-view trajectory
    using front-view data length as reference.
    """
    n = len(front_positions)

    # Horizontal motion toward stumps
    x = np.linspace(100, 450, n)

    # Parabolic vertical motion (gravity approximation)
    a = 0.002
    b = -0.9
    c = 350
    y = a * x**2 + b * x + c

    return x, y
