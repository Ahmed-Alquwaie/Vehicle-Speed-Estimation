from ultralytics import YOLO
import cv2
import numpy as np
import math
import json
import os
from datetime import datetime

# =========================
# Resource Path
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    return os.path.join(BASE_DIR, relative_path)

# =========================
# LOAD CALIBRATION
# =========================

with open(resource_path("configs/calibration.json"), "r") as f:
    calibration = json.load(f)

video_path = calibration["video_path"]
road_points = calibration["road_points"]
meter_per_pixel = calibration["meter_per_pixel"]

print("Video:", video_path)
print("Meter Per Pixel:", meter_per_pixel)

# =========================
# MODEL
# =========================

model = YOLO(resource_path("models/yolov8s.pt"))

# =========================
# VIDEO
# =========================

cap = cv2.VideoCapture(video_path)


fps = cap.get(cv2.CAP_PROP_FPS)

# =========================
# OUTPUT VIDEO
# =========================

outputs_dir = resource_path("outputs")

os.makedirs(outputs_dir, exist_ok=True)

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

output_path = os.path.join(
    outputs_dir,
    f"result_{timestamp}.mp4"
)

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

out = cv2.VideoWriter(
    output_path,
    fourcc,
    fps,
    (frame_width, frame_height)
)
#=======================================
if fps == 0:
    fps = 30

# =========================
# HOMOGRAPHY
# =========================

pts_src = np.float32(road_points)

W = 600
H = 600

pts_dst = np.float32([
    [0, 0],
    [W, 0],
    [0, H],
    [W, H]
])

M = cv2.getPerspectiveTransform(
    pts_src,
    pts_dst
)

# =========================
# TRACK DATA
# =========================

track_history = {}
speed_history = {}

# =========================
# MAIN LOOP
# =========================

while cap.isOpened():

    ret, frame = cap.read()

    if not ret:
        break

    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        classes=[2, 3, 5, 7],
        conf=0.4,
        verbose=False
    )

    annotated = frame.copy()

    if results[0].boxes.id is not None:

        boxes = results[0].boxes.xyxy.cpu()
        ids = results[0].boxes.id.int().cpu().tolist()

        for box, track_id in zip(boxes, ids):

            x1, y1, x2, y2 = box

            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            point = np.array(
                [[[cx, cy]]],
                dtype=np.float32
            )

            warped = cv2.perspectiveTransform(
                point,
                M
            )

            wx, wy = warped[0][0]

            cv2.circle(
                annotated,
                (cx, cy),
                4,
                (0, 0, 255),
                -1
            )

            if track_id in track_history:

                px, py = track_history[track_id]

                dist_pixels = math.sqrt(
                    (wx - px) ** 2 +
                    (wy - py) ** 2
                )

                speed_mps = (
                    dist_pixels *
                    meter_per_pixel *
                    fps
                )

                speed_kmh = speed_mps * 3.6

                # =========================
                # SMOOTHING
                # =========================

                if track_id not in speed_history:
                    speed_history[track_id] = []

                speed_history[track_id].append(
                    speed_kmh
                )

                if len(speed_history[track_id]) > 12:
                    speed_history[track_id].pop(0)

                speed_kmh = (
                    sum(speed_history[track_id]) /
                    len(speed_history[track_id])
                )

                speed_kmh = max(
                    0,
                    min(speed_kmh, 200)
                )

                cv2.putText(
                    annotated,
                    f"{int(speed_kmh)} km/h",
                    (cx, cy - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

            track_history[track_id] = (
                wx,
                wy
            )

    cv2.imshow(
        "Vehicle Speed Estimation",
        annotated
    )
    out.write(annotated)

    if cv2.waitKey(20) & 0xFF == ord("q"):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

print("\nVideo saved successfully.")
print(output_path)