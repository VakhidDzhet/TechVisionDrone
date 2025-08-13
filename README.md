Tech Vision Project

Соответствие требованиям:
Видеопоток: поддержаны источники webcam, file, rtsp://…, udp://…. Почему так? Работу выполнял на макбуке, и делал все по этапно.
GStreamer используется для RTSP/UDP, если поддерживается сборкой OpenCV; иначе — FFmpeg (RTSP/UDP-TS).
Детекция: YOLOv8 (Ultralytics).
Отображение: OpenCV overlay — прямоугольники и метки классов в реальном времени.
Лог: CSV (timestamp,class_id,score,x_min,y_min,x_max,y_max).
Трекинг: OpenCV трекеры (CSRT/KCF/MOSSE) с авто-фолбэком; частота детекций регулируется (--detect-every).
PWM: пропорциональный регулятор + deadband + EMA-сглаживание; печать команд YAW/ROLL.
Проверено на Python 3.9. Код кроссплатформенный (Linux/Windows/macOS).

--------
Требования и установка
Рекомендуется virtualenv.

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -V
pip install --upgrade pip setuptools wheel

--------
Пакеты (без конфликтов NumPy/OpenCV)
Вариант по умолчанию (стабильный для трекеров OpenCV):

pip install numpy==1.26.4
pip install opencv-contrib-python==4.9.0.80
pip install ultralytics torch torchvision torchaudio

Если хотите остаться на NumPy 2.x — попробуйте opencv-contrib-python>=4.10.*.

--------
GStreamer (для RTSP/UDP через OpenCV GStreamer backend)
Linux (Ubuntu/Debian):
sudo apt-get install -y gstreamer1.0-tools \
  gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly

macOS (Homebrew):
brew install gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly

--------
Старт!
1) Веб-камера
python Main.py --source 0

2) Локальный файл
python Main.py --source demo.mp4

3) UDP
UDP/RTP/H.264 через GStreamer (если поддерживается):
Передатчик (терминал №1):
gst-launch-1.0 -v filesrc location="demo.mp4" ! decodebin ! videoconvert ! \
  x264enc tune=zerolatency speed-preset=ultrafast bitrate=2000 key-int-max=30 ! \
  h264parse config-interval=1 ! rtph264pay pt=96 ! \
  udpsink host=127.0.0.1 port=5600

Приёмник (терминал №2):
python Main.py --source "udp://@127.0.0.1:5600" --use-gst

4) Эмуляция RTSP (локальный RTSP-сервер из файла)
gst-rtsp-launch "( filesrc location=demo.mp4 ! decodebin ! videoconvert ! \
  x264enc tune=zerolatency speed-preset=ultrafast bitrate=2000 key-int-max=30 ! \
  h264parse config-interval=1 ! rtph264pay name=pay0 pt=96 )"

python Main.py --source "rtsp://127.0.0.1:8554/test"

--------
Лог и формат CSV
utils/logger.py пишет detections.csv в корень.
Столбцы:

[timestamp, class_id, score, x_min, y_min, x_max, y_max]

--------
PWM-контроллер
control/controller.py: P-контроллер переводит смещение центра бокса от центра кадра в PWM-команды Yaw/Roll.

Нейтраль: 1500, диапазон: ±max_delta (по умолчанию 300 → 1200..1800)

Настройки: deadband_px, k (чувствительность), ema_alpha (сглаживание)

Функция send_command(yaw, roll) — по умолчанию печатает в консоль (можно заменить на отправку в MAVLink RC override).

--------
Тесты
1) Проверка PWM
python tests/test_controller.py
Ожидание: три строки PWM и PWM math: OK.

2) Проверка формата детекций
python tests/test_detector_one_image.py  # отредактируйте путь к sample.jpg внутри
Ожидание: формат кортежей (x1,y1,x2,y2,cls,score) корректный.

3) Проверка логгера
python tests/test_logger.py
Ожидание: создаётся test_detections.csv, первая строка — заголовок, вторая — корректные данные (время в ISO-формате).
