def lbw_decision(side_x, side_y, impact_x_front):
    # Side-view stump region
    stump_x_side = (400, 430)
    stump_y_side = (200, 450)

    # Front-view stump alignment
    stump_x_front = (300, 340)

    # Check if predicted side-view hits stumps
    hits_stumps = any(
        stump_x_side[0] <= x <= stump_x_side[1] and
        stump_y_side[0] <= y <= stump_y_side[1]
        for x, y in zip(side_x, side_y)
    )

    # Check impact line from front view
    impact_inline = stump_x_front[0] <= impact_x_front <= stump_x_front[1]

    if hits_stumps and impact_inline:
        return "OUT"
    else:
        return "NOT OUT"
