# games/pong/ai.py
# MicroPython-compatible. Simple AI paddle controller.


class PaddleAI:
    """
    Tracks the ball's y position with a configurable reaction delay.
    Higher delay = easier AI. Lower delay = harder.
    """

    def __init__(self, paddle, reaction_delay_ms=80):
        self._paddle = paddle
        self._reaction_delay = reaction_delay_ms
        self._timer = 0

    def update(self, dt, ball):
        """Move the AI paddle towards the ball's y position."""
        self._timer += dt
        if self._timer < self._reaction_delay:
            return
        self._timer = 0

        ball_y    = ball.pixel_y
        paddle_cy = self._paddle.center_y

        if ball_y < paddle_cy:
            self._paddle.move_up(dt)
        elif ball_y > paddle_cy:
            self._paddle.move_down(dt)
