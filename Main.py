import argparse
import cv2
from typing import List, Optional

from video.video_stream import VideoStream
from detecting.detector import Detector
from tracking.tracker import TrackerCSRT
from utils.logger import Logger
from control.controller import Controller

def parse_classes(s: Optional[str], all_names: dict) -> Optional[List[int]]:
    if not s:
        return None
    items = [x.strip() for x in s.split(",")]
    ids = []
    name_to_id = {v: k for k, v in all_names.items()}
    for x in items:
        if not x:
            continue
        if x.isdigit():
            ids.append(int(x))
        else:
            if x in name_to_id:
                ids.append(int(name_to_id[x]))
            else:
                print(f"[WARN] Unknown class name: {x} (ignored)")
    return ids or None

def build_argparser():
    p = argparse.ArgumentParser(description="RTSP/GStreamer + YOLOv8 + Tracking + PWM demo")
    p.add_argument("--source", type=str, default="0",
                   help="Камера индекс (например '0'), файл 'demo.mp4' или RTSP/UDP строка")
    p.add_argument("--use-gst", action="store_true",
                   help="Принудительно использовать GStreamer (для RTSP/UDP обычно не нужно указывать)")
    p.add_argument("--conf", type=float, default=0.35, help="Confidence threshold")
    p.add_argument("--iou", type=float, default=0.45, help="NMS IoU threshold")
    p.add_argument("--imgsz", type=int, default=640, help="Входной размер модели (кратно 32)")
    p.add_argument("--classes", type=str, default=None,
                   help="Список классов через запятую (id или имена), напр. 'person,car' или '0,2'")
    p.add_argument("--device", type=str, default=None,
                   help="cpu|mps|cuda; по умолчанию определяется автоматически")
    p.add_argument("--detect-every", type=int, default=5,
                   help="Детектировать каждые N кадров, между ними использовать трекер")
    return p

def main():
    args = build_argparser().parse_args()

    source = int(args.source) if args.source.isdigit() else args.source

    stream = VideoStream(source, use_gstreamer=args.use_gst)

    frame = stream.read_frame()
    if frame is None:
        raise RuntimeError("No frames from source")
    h, w = frame.shape[:2]

    detector = Detector(model_path="yolov8n.pt",
                        conf=args.conf, iou=args.iou,
                        imgsz=args.imgsz, classes=None,
                        device=args.device)

    classes_filter = parse_classes(args.classes, detector.names)

    logger = Logger(log_file="detections.csv")
    controller = Controller(frame_width=w, frame_height=h,
                            center_pwm=1500, max_delta=300,
                            deadband_px=12, k=0.30, ema_alpha=0.25)

    tracker = TrackerCSRT()
    frame_idx = 0
    target_bbox = None

    while True:
        frame = stream.read_frame()
        if frame is None:
            cv2.waitKey(5)
            continue

        frame_idx += 1

        use_detection = (frame_idx % max(1, args.detect_every) == 0) or (not tracker.active)

        if use_detection:
            detections = detector.detect(frame)

            if classes_filter is not None:
                detections = [d for d in detections if d[4] in classes_filter]

            target_bbox = None
            max_area = 0
            for (x1, y1, x2, y2, cls, score) in detections:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = str(detector.names.get(cls, cls))
                cv2.putText(frame, f"{label}:{score:.2f}", (x1, max(0, y1 - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                logger.log(cls, score, x1, y1, x2, y2)
                area = max(0, (x2 - x1)) * max(0, (y2 - y1))
                if area > max_area:
                    max_area = area
                    target_bbox = (x1, y1, x2, y2)

            if target_bbox is not None:
                tracker.init(frame, target_bbox)

        else:
            tb = tracker.update(frame)
            if tb is not None:
                x1, y1, x2, y2 = tb
                target_bbox = tb
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 255), 2)
                cv2.putText(frame, "tracked", (x1, max(0, y1 - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)
                logger.log(-1, 1.0, x1, y1, x2, y2)
            else:
                target_bbox = None

        if target_bbox is not None:
            controller.control_from_bbox(*target_bbox)

        cv2.imshow("Detections + Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stream.release()

if __name__ == "__main__":
    main()