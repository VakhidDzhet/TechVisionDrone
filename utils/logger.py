import csv
from datetime import datetime

class Logger:
    def __init__(self, log_file="detections.csv"):
        self.log_file = log_file
        with open(self.log_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "class_id", "score", "x_min", "y_min", "x_max", "y_max"])

    def log(self, class_id, score, x1, y1, x2, y2):
        with open(self.log_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now().isoformat(), class_id, f"{score:.3f}", x1, y1, x2, y2])