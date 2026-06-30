def detect_bounce(ball_positions):
    for i in range(1, len(ball_positions) - 1):
        if ball_positions[i][1] > ball_positions[i-1][1] and \
           ball_positions[i][1] > ball_positions[i+1][1]:
            return ball_positions[i]

    return None
