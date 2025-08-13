import math

def send_command(yaw, roll):
    print(f"YAW PWM: {yaw} ROLL PWM: {roll}")

class _EMA:
    def __init__(self, alpha=0.25):
        self.a = alpha
        self.v = None
    def filter(self, x: int) -> int:
        if self.v is None:
            self.v = float(x)
        else:
            self.v = self.a * float(x) + (1.0 - self.a) * self.v
        return int(self.v)

class Controller:
    def __init__(self, frame_width, frame_height,
                 center_pwm=1500, max_delta=300,
                 deadband_px=10, k=0.25, ema_alpha=0.25):
        self.cx = frame_width // 2
        self.cy = frame_height // 2
        self.center = center_pwm
        self.max_delta = max_delta
        self.deadband = deadband_px
        self.k = k
        self.ema_yaw = _EMA(ema_alpha)
        self.ema_roll = _EMA(ema_alpha)

    def _pwm_from_error(self, err_norm):
        pwm = int(self.center + self.k * err_norm * self.max_delta)
        return max(self.center - self.max_delta, min(self.center + self.max_delta, pwm))

    def control_from_bbox(self, x1, y1, x2, y2):
        bx = (x1 + x2) // 2
        by = (y1 + y2) // 2

        ex_px = bx - self.cx
        ey_px = by - self.cy

        if abs(ex_px) < self.deadband:
            ex_px = 0
        if abs(ey_px) < self.deadband:
            ey_px = 0

        ex_norm = ex_px / max(1, self.cx)
        ey_norm = ey_px / max(1, self.cy)

        yaw_pwm  = self._pwm_from_error(ex_norm)
        roll_pwm = self._pwm_from_error(ey_norm)

        # сглаживание
        yaw_pwm  = self.ema_yaw.filter(yaw_pwm)
        roll_pwm = self.ema_roll.filter(roll_pwm)

        send_command(yaw_pwm, roll_pwm)
        return yaw_pwm, roll_pwm