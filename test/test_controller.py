from control.controller import Controller

def check():
    w, h = 1280, 720
    ctrl = Controller(w, h, center_pwm=1500, max_delta=300, deadband_px=0, k=0.3)

    yaw, roll = ctrl.control_from_bbox(w//2-10, h//2-10, w//2+10, h//2+10)
    print("center:", yaw, roll); assert yaw==1500 and roll==1500

    yaw, roll = ctrl.control_from_bbox(100, h//2-50, 200, h//2+50)
    print("left:", yaw, roll); assert yaw < 1500

    yaw, roll = ctrl.control_from_bbox(w-200, h//2-50, w-100, h//2+50)
    print("right:", yaw, roll); assert yaw > 1500

if __name__ == "__main__":
    check(); print("PWM math: OK")