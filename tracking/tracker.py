import cv2
from typing import Optional, Tuple

class TrackerCSRT:

    def __init__(self):
        self.tracker = None
        self.active = False

    @staticmethod
    def _create_csrt():
        # Совместимость разных сборок OpenCV
        if hasattr(cv2, "legacy") and hasattr(cv2.legacy, "TrackerCSRT_create"):
            return cv2.legacy.TrackerCSRT_create()
        if hasattr(cv2, "TrackerCSRT_create"):
            return cv2.TrackerCSRT_create()
        raise RuntimeError("TrackerCSRT is not available in this OpenCV build")

    @staticmethod
    def _xyxy_to_xywh(bbox_xyxy):
        x1, y1, x2, y2 = bbox_xyxy
        return (x1, y1, x2 - x1, y2 - y1)

    @staticmethod
    def _xywh_to_xyxy(bbox_xywh):
        x, y, w, h = bbox_xywh
        return (int(x), int(y), int(x + w), int(y + h))

    def init(self, frame, bbox_xyxy) -> bool:
        self.tracker = self._create_csrt()
        ok = self.tracker.init(frame, self._xyxy_to_xywh(bbox_xyxy))
        self.active = bool(ok)
        return self.active

    def update(self, frame) -> Optional[Tuple[int,int,int,int]]:
        if not self.active or self.tracker is None:
            return None
        ok, bbox_xywh = self.tracker.update(frame)
        if not ok:
            self.active = False
            return None
        return self._xywh_to_xyxy(bbox_xywh)

    def clear(self):
        self.tracker = None
        self.active = False