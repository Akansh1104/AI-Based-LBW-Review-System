import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

from preprocess import read_video
from tracking import track_ball
from trajectory import simulate_side_view
from stump_logic import lbw_decision


# -------------------------------------------------
# CONFIG
# -------------------------------------------------
FRONT_VIDEO = "../Data/front_view.mp4"
RESULTS_DIR = "../Results"
os.makedirs(RESULTS_DIR, exist_ok=True)


# -------------------------------------------------
# FRONT VIEW VISUALIZATION (2D)
# -------------------------------------------------
def plot_front_view_movement(front_positions, impact_x):
    stump_x = (300, 340)

    x_vals = [p[0] for p in front_positions]
    y_vals = list(range(len(front_positions)))

    plt.figure(figsize=(8, 5))
    plt.style.use("seaborn-v0_8-whitegrid")

    plt.plot(
        x_vals, y_vals,
        color="#6A0DAD",
        linewidth=2.5,
        marker="o",
        label="Ball Movement (Front View)"
    )

    plt.axvspan(
        stump_x[0], stump_x[1],
        color="green", alpha=0.25,
        label="Stump Line (Inline Zone)"
    )

    plt.scatter(
        impact_x, y_vals[-1],
        color="black", s=120, marker="X",
        label="Impact Point"
    )

    status = "INLINE" if stump_x[0] <= impact_x <= stump_x[1] else "MISSING"
    color = "green" if status == "INLINE" else "red"

    plt.text(
        0.02, 0.94,
        f"Impact Line: {status}",
        transform=plt.gca().transAxes,
        fontsize=12, fontweight="bold",
        color=color,
        bbox=dict(facecolor="white", edgecolor="black")
    )

    plt.xlabel("Horizontal Position (pixels)")
    plt.ylabel("Time (Frame Index)")
    plt.title("Front View – Ball Movement & Impact Line", fontweight="bold")
    plt.legend()
    plt.tight_layout()
    plt.show()


# -------------------------------------------------
# SIDE VIEW VISUALIZATION (2D)
# -------------------------------------------------
def plot_side_view(side_x, side_y, decision):
    plt.figure(figsize=(10, 6))
    plt.style.use("seaborn-v0_8-whitegrid")

    plt.plot(
        side_x, side_y,
        linestyle="--", linewidth=3,
        color="crimson",
        label="Simulated Side-View Trajectory"
    )

    plt.axvspan(
        400, 430,
        color="green", alpha=0.25,
        label="Stump Region"
    )

    plt.scatter(
        side_x[-1], side_y[-1],
        color="black", s=120, marker="X",
        label="Predicted Impact Point"
    )

    plt.text(
        0.02, 0.95,
        f"LBW Decision: {decision}",
        transform=plt.gca().transAxes,
        fontsize=13, fontweight="bold",
        bbox=dict(facecolor="white", edgecolor="black")
    )

    plt.xlabel("Horizontal Distance (towards stumps)")
    plt.ylabel("Ball Height")
    plt.title("Side View – Trajectory & Wicket Collision", fontweight="bold")
    plt.gca().invert_yaxis()
    plt.legend()
    plt.tight_layout()

    plt.savefig(f"{RESULTS_DIR}/lbw_analysis.png", dpi=300)
    plt.show()


# -------------------------------------------------
# STATIC 3D TRAJECTORY
# -------------------------------------------------
def plot_3d_trajectory(side_x, side_y, decision):
    z = np.arange(len(side_x))

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")

    ax.plot(
        side_x, side_y, z,
        color="crimson", linewidth=3,
        label="Ball Trajectory"
    )

    ax.scatter(
        side_x[-1], side_y[-1], z[-1],
        color="black", s=80, marker="X",
        label="Impact Point"
    )

    for sx in [400, 430]:
        ax.plot(
            [sx]*20,
            np.linspace(200, 450, 20),
            np.linspace(0, z[-1], 20),
            color="green", alpha=0.4
        )

    ax.set_xlabel("Horizontal Distance")
    ax.set_ylabel("Ball Height")
    ax.set_zlabel("Time (frames)")
    ax.set_title(
        f"3D Ball Trajectory (Space–Time)\nLBW Decision: {decision}",
        fontweight="bold"
    )

    ax.legend()
    plt.tight_layout()
    plt.show()


# -------------------------------------------------
# ANIMATED 3D TRAJECTORY
# -------------------------------------------------
def animate_3d_trajectory_realistic(side_x, side_y, decision):
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib.animation import FuncAnimation

    # Time axis
    t = np.linspace(0, 1, len(side_x))

    # Smooth forward motion (slight deceleration)
    x = side_x * (1 - 0.05 * t)

    # Gravity-affected vertical motion
    y = side_y + 40 * (t ** 2)

    # Depth axis (time → depth illusion)
    z = t * 200

    fig = plt.figure(figsize=(11, 7))
    ax = fig.add_subplot(111, projection="3d")

    # ---------------- Pitch Plane ----------------
    pitch_x = np.linspace(min(x)-50, max(x)+50, 10)
    pitch_z = np.linspace(0, 200, 10)
    pitch_X, pitch_Z = np.meshgrid(pitch_x, pitch_z)
    pitch_Y = np.full_like(pitch_X, max(y)+10)

    ax.plot_surface(
        pitch_X, pitch_Y, pitch_Z,
        color="#d2b48c", alpha=0.3
    )

    # ---------------- Stumps (3D Wicket) ----------------
    stump_x = [400, 415, 430]
    stump_y = np.linspace(max(y)-80, max(y)+10, 20)
    stump_z = np.linspace(150, 200, 20)

    for sx in stump_x:
        ax.plot(
            [sx]*20, stump_y, stump_z,
            color="green", linewidth=4
        )

    # ---------------- Ball Path ----------------
    line, = ax.plot([], [], [], color="crimson", linewidth=3)
    ball = ax.scatter([], [], [], color="black", s=70)

    ax.set_xlim(min(x)-50, max(x)+50)
    ax.set_ylim(max(y)+30, min(y)-30)
    ax.set_zlim(0, 220)

    ax.set_xlabel("Pitch Length (towards stumps)")
    ax.set_ylabel("Ball Height")
    ax.set_zlabel("Depth / Time")

    ax.set_title(
        f"Cricket-Style 3D Ball Trajectory\nLBW Decision: {decision}",
        fontsize=14,
        fontweight="bold"
    )

    # Camera angle (important for realism)
    ax.view_init(elev=18, azim=-60)

    def update(i):
        line.set_data(x[:i], y[:i])
        line.set_3d_properties(z[:i])

        ball._offsets3d = ([x[i]], [y[i]], [z[i]])
        return line, ball

    FuncAnimation(
        fig,
        update,
        frames=len(x),
        interval=70,
        blit=False
    )

    plt.tight_layout()
    plt.show()



# -------------------------------------------------
# MAIN PIPELINE
# -------------------------------------------------
front_frames = read_video(FRONT_VIDEO)
front_positions = track_ball(front_frames)

if len(front_positions) < 5:
    print("Ball not detected clearly in front-view video.")
    exit()

impact_x_front = front_positions[-1][0]

side_x, side_y = simulate_side_view(front_positions)

decision = lbw_decision(side_x, side_y, impact_x_front)

print("Front-view Impact X:", impact_x_front)
print("LBW Decision:", decision)

plot_front_view_movement(front_positions, impact_x_front)
plot_side_view(side_x, side_y, decision)
plot_3d_trajectory(side_x, side_y, decision)
animate_3d_trajectory_realistic(side_x, side_y, decision)

