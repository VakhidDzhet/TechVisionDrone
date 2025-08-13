from typing import Optional
from ultralytics import YOLO
import torch

class Detector:
    def __init__(self,
                 model_path: str = "yolov8n.pt",
                 conf: float = 0.35,
                 iou: float = 0.45,
                 imgsz: int = 640,
                 classes=None,
                 device: Optional[str] = None):
        self.model = YOLO(model_path)

        if device is None:
            if torch.backends.mps.is_available():
                device = "mps"
            elif torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"

        self.device = device
        self.model.to(self.device)

        self.conf = conf
        self.iou = iou
        self.imgsz = imgsz
        self.classes = classes

    def detect(self, frame):
        results = self.model.predict(
            source=frame,
            conf=self.conf,
            iou=self.iou,
            imgsz=self.imgsz,
            classes=self.classes,
            device=self.device,
            verbose=False
        )

        detections = []
        r = results[0]
        boxes = getattr(r, "boxes", None)
        if boxes is None:
            return detections

        for b in boxes:
            x1, y1, x2, y2 = [int(v) for v in b.xyxy[0].tolist()]
            cls_id = int(b.cls[0].item())
            score = float(b.conf[0].item())
            detections.append((x1, y1, x2, y2, cls_id, score))
        return detections

    @property
    def names(self):
        return self.model.names