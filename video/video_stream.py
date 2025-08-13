import time
import cv2
from typing import Union

# class VideoStream:
#     def __init__(self, source, warmup_frames: int = 5):
#         self.cap = cv2.VideoCapture(source)
#         if not self.cap.isOpened():
#             raise RuntimeError(f"Cannot open video source: {source}")
#
#         for _ in range(warmup_frames):
#             self.cap.read()
#             time.sleep(0.02)
#
#     def read_frame(self):
#         ret, frame = self.cap.read()
#         if not ret:
#             return None
#         return frame
#
#     def release(self):
#         self.cap.release()
#         cv2.destroyAllWindows()

class VideoStream:
    def __init__(self,
                 source: Union[int, str],
                 warmup_frames: int = 5,
                 use_gstreamer: bool = None,
                 max_fail_reads: int = 50,
                 reconnect_delay_s: float = 0.5):
        self.source = source
        self.warmup_frames = warmup_frames
        self.max_fail_reads = max_fail_reads
        self.reconnect_delay_s = reconnect_delay_s
        self.fail_reads = 0

        if use_gstreamer is None:
            self.use_gst = isinstance(source, str) and (
                source.startswith("rtsp://") or
                source.startswith("rtsps://") or
                source.startswith("udp://")
            )
        else:
            self.use_gst = use_gstreamer

        self.cap = self._open()

    def _build_gst_pipeline(self) -> str:
        s = str(self.source)
        if s.startswith("rtsp://") or s.startswith("rtsps://"):
            # RTSP (H.264) -> OpenCV
            return (
                f"rtspsrc location={s} protocols=tcp latency=0 ! "
                f"rtph264depay ! h264parse ! avdec_h264 ! "
                f"videoconvert ! appsink drop=true sync=false"
            )
        if s.startswith("udp://"):
            # Пример под H.264 RTP в UDP; под свой поток настрой caps
            return (
                f"udpsrc uri={s} ! application/x-rtp, media=video, encoding-name=H264, payload=96 ! "
                f"rtph264depay ! h264parse ! avdec_h264 ! "
                f"videoconvert ! appsink drop=true sync=false"
            )
        # На всякий, возвращаем s — но сюда попадать не должны
        return s

    def _open(self) -> cv2.VideoCapture:
        if self.use_gst:
            pipeline = self._build_gst_pipeline()
            cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
        else:
            cap = cv2.VideoCapture(self.source)

        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video source: {self.source}")

        # Прогрев (первые кадры часто пустые)
        for _ in range(self.warmup_frames):
            cap.read()
            time.sleep(0.02)
        self.fail_reads = 0
        return cap

    def _reconnect(self):
        try:
            self.cap.release()
        except Exception:
            pass
        time.sleep(self.reconnect_delay_s)
        self.cap = self._open()

    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.fail_reads += 1
            if self.use_gst and self.fail_reads >= self.max_fail_reads:
                # Пробуем переподключиться
                self._reconnect()
                ret, frame = self.cap.read()
                if not ret:
                    return None
            else:
                return None
        else:
            self.fail_reads = 0
        return frame

    def release(self):
        try:
            self.cap.release()
        finally:
            cv2.destroyAllWindows()