import cv2
from detecting.detector import Detector

def test_one_image(path="car_man.jpg"):
    img = cv2.imread(path)
    assert img is not None, f"Не смог открыть {path}"

    det = Detector(model_path="yolov8n.pt", conf=0.25, imgsz=640)
    dets = det.detect(img)

    print(f"Нашли {len(dets)} объектов")
    for d in dets:
        assert isinstance(d, tuple) and len(d) == 6
        x1,y1,x2,y2,cls,score = d
        assert all(isinstance(v, int) for v in (x1,y1,x2,y2))
        assert isinstance(cls, int)
        assert isinstance(score, float)
    print("Формат детекций: OK")

if __name__ == "__main__":
    test_one_image()