import csv
from datetime import datetime
from utils.logger import Logger

def check_logger():
    log = Logger("test_detections.csv")
    log.log(0, 0.91, 10, 20, 110, 220)

    with open("test_detections.csv", newline="") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["timestamp","class_id","score","x_min","y_min","x_max","y_max"]
    ts, cls, score, x1, y1, x2, y2 = rows[1]
    datetime.fromisoformat(ts)      # парсится как ISO
    float(score); int(cls); int(x1); int(y1); int(x2); int(y2)
    print("Логгер/CSV: OK")

if __name__ == "__main__":
    check_logger()