from ball_detection import detect_ball

def track_ball(frames):
    positions = []

    for frame in frames:
        pos = detect_ball(frame)
        if pos:
            positions.append(pos)

    return positions
