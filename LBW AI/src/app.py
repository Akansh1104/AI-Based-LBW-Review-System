import streamlit as st
import matplotlib.pyplot as plt

from preprocess import read_video
from tracking import track_ball
from trajectory import simulate_side_view

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
FRONT_VIDEO = "../Data/front_view.mp4"

STUMP_X_FRONT = (300, 340)
STUMP_X_SIDE = (400, 430)
STUMP_Y_SIDE = (200, 450)

st.set_page_config(layout="wide")
st.title("AI-Based LBW Review System")

# -------------------------------------------------
# PROCESS VIDEO
# -------------------------------------------------
frames = read_video(FRONT_VIDEO)
front_positions = track_ball(frames)

if len(front_positions) < 5:
    st.error("Ball not detected clearly in the video.")
    st.stop()

impact_x = front_positions[-1][0]
impact_inline = STUMP_X_FRONT[0] <= impact_x <= STUMP_X_FRONT[1]

side_x, side_y = simulate_side_view(front_positions)

hits_stumps = any(
    STUMP_X_SIDE[0] <= x <= STUMP_X_SIDE[1] and
    STUMP_Y_SIDE[0] <= y <= STUMP_Y_SIDE[1]
    for x, y in zip(side_x, side_y)
)

decision = "OUT" if impact_inline and hits_stumps else "NOT OUT"

# -------------------------------------------------
# SUMMARY (MATCHES LOGIC)
# -------------------------------------------------
st.subheader("🏏 LBW Decision Summary")

colA, colB, colC = st.columns(3)

colA.metric(
    "Impact Check",
    "INLINE" if impact_inline else "OUTSIDE",
    delta="With Stumps" if impact_inline else "Not With Stumps"
)

colB.metric(
    "Wicket Check",
    "HITS" if hits_stumps else "MISSES",
    delta="Would Hit Stumps" if hits_stumps else "Would Miss Stumps"
)

colC.metric(
    "LBW Decision",
    "OUT" if decision == "OUT" else "NOT OUT"
)

st.markdown("---")


# -------------------------------------------------
# VISUALS (SMALL & SIDE-BY-SIDE)
# -------------------------------------------------
col1, col2 = st.columns(2)

# ---------- FRONT VIEW ----------
# ---------- FRONT VIEW (CRICKET-REALISTIC) ----------
with col1:
    st.subheader("Front View – Impact in Line with Stumps")

    st.markdown("""
    **How to read this view (like an umpire):**
    - Green area = width of the three stumps
    - ❌ X = where the ball hit the pad
    - Left / Right = off-side or leg-side
    """)

    fig1, ax1 = plt.subplots(figsize=(4.5, 3.2))

    # Draw pitch baseline
    ax1.axhline(0, color="saddlebrown", linewidth=2)

    # Stump zone (front view)
    ax1.axvspan(
        STUMP_X_FRONT[0],
        STUMP_X_FRONT[1],
        color="green",
        alpha=0.3,
        label="Stump Line"
    )

    # Individual stumps (visual realism)
    stump_centers = [
        STUMP_X_FRONT[0] + 5,
        (STUMP_X_FRONT[0] + STUMP_X_FRONT[1]) / 2,
        STUMP_X_FRONT[1] - 5
    ]
    for s in stump_centers:
        ax1.plot([s, s], [0, 0.15], color="darkgreen", linewidth=4)

    # Impact point
    ax1.scatter(
        impact_x,
        0.08,
        color="black",
        s=100,
        marker="X",
        zorder=5,
        label="Ball Impact"
    )

    # Labels for cricket understanding
    ax1.text(STUMP_X_FRONT[0] - 25, -0.08, "LEG SIDE", fontsize=9)
    ax1.text(STUMP_X_FRONT[1] + 5, -0.08, "OFF SIDE", fontsize=9)
    ax1.text(
        (STUMP_X_FRONT[0] + STUMP_X_FRONT[1]) / 2 - 10,
        -0.15,
        "MIDDLE",
        fontsize=9
    )

    # Axis cleanup (cricket-style)
    ax1.set_ylim(-0.25, 0.25)
    ax1.set_yticks([])
    ax1.set_xlabel("Left  ←  Pitch Centre  →  Right")
    ax1.set_title(
        "IMPACT INLINE" if impact_inline else "IMPACT OUTSIDE LINE",
        color="green" if impact_inline else "red",
        fontweight="bold"
    )

    ax1.legend(loc="upper center", fontsize=8)
    st.pyplot(fig1)


# ---------- SIDE VIEW ----------
# ---------- SIDE VIEW (CRICKET-REALISTIC) ----------
with col2:
    st.subheader("Side View – Would the Ball Hit the Stumps?")

    st.markdown("""
    **How to read this view (like an umpire):**
    - Brown line = pitch
    - Green lines = stumps
    - Red dashed line = predicted ball path
    - ❌ X = point where ball reaches the stumps
    """)

    fig2, ax2 = plt.subplots(figsize=(4.5, 3.2))

    # Pitch line
    ax2.axhline(0, color="saddlebrown", linewidth=2)

    # Stumps (side view – 3 vertical sticks)
    stump_x_positions = [
        (STUMP_X_SIDE[0] + STUMP_X_SIDE[1]) / 2 - 5,
        (STUMP_X_SIDE[0] + STUMP_X_SIDE[1]) / 2,
        (STUMP_X_SIDE[0] + STUMP_X_SIDE[1]) / 2 + 5,
    ]

    for sx in stump_x_positions:
        ax2.plot(
            [sx, sx],
            [0, 1.2],
            color="green",
            linewidth=4
        )

    # Ball trajectory
    ax2.plot(
        side_x,
        side_y / max(side_y),
        "--",
        color="red",
        linewidth=2.5,
        label="Predicted Ball Path"
    )

    # Impact point at stump plane
    ax2.scatter(
        side_x[-1],
        side_y[-1] / max(side_y),
        color="black",
        s=90,
        marker="X",
        zorder=5,
        label="Ball at Stumps"
    )

    # Axis styling (cricket-like)
    ax2.set_xlabel("Distance Towards Stumps")
    ax2.set_ylabel("Ball Height")
    ax2.set_ylim(-0.2, 1.4)
    ax2.set_yticks([])

    ax2.set_title(
        "BALL HITS STUMPS" if hits_stumps else "BALL MISSES STUMPS",
        color="green" if hits_stumps else "red",
        fontweight="bold"
    )

    ax2.legend(loc="upper left", fontsize=8)
    st.pyplot(fig2)

# -------------------------------------------------
# FINAL EXPLANATION (MATCHED)
# -------------------------------------------------
st.info(
    f"""
**LBW DECISION EXPLANATION:**

• Impact Check: **{"IMPACT INLINE WITH STUMPS" if impact_inline else "IMPACT OUTSIDE LINE"}**  
• Wicket Check: **{"BALL WOULD HIT STUMPS" if hits_stumps else "BALL WOULD MISS STUMPS"}**  

👉 **FINAL LBW DECISION: {decision}**
"""
)


