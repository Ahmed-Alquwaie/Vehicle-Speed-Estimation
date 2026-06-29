import cv2
import json
import math
import os
from tkinter import Tk, filedialog, simpledialog, messagebox

# =====================================
# Resource Path
# =====================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    return os.path.join(BASE_DIR, relative_path)

# =====================================
# Globals
# =====================================

clicked_points = []
frame_copy = None
# =====================================
# Draw Text
# =====================================

def draw_text(image,
              text,
              position,
              color=(255,255,255),
              scale=0.7,
              thickness=2):

    x, y = position

    # Shadow
    cv2.putText(
        image,
        text,
        (x + 2, y + 2),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        (0, 0, 0),
        thickness + 3,
        cv2.LINE_AA
    )

    # Main Text
    cv2.putText(
        image,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness,
        cv2.LINE_AA
    )


# =====================================
# Mouse Click
# =====================================

def mouse_click(event, x, y, flags, param):

    global clicked_points, frame_copy

    if event == cv2.EVENT_LBUTTONDOWN:

        clicked_points.append([x, y])

        print(f"Point {len(clicked_points)}: {x}, {y}")

        cv2.circle(frame_copy, (x, y), 5, (0, 0, 255), -1)

        draw_text(
            frame_copy,
            str(len(clicked_points)),
            (x + 10, y - 10),
            (0, 255, 0),
            0.7,
            2
        )


# =====================================
# Select N Points
# =====================================

def select_points(frame, window_name, point_names):

    global clicked_points, frame_copy

    clicked_points = []
    frame_copy = frame.copy()

    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_click)

    while True:

        display = frame_copy.copy()

        # عنوان المرحلة
        draw_text(
            display,
            window_name,
            (20, 35),
            (0,255,255),
            0.9,
            2
        )

        # تعليمات
        for i, name in enumerate(point_names):

            if i < len(clicked_points):

                text = f"[✓] {name}"
                color = (0, 255, 0)

            elif i == len(clicked_points):

                text = f"--> Click: {name}"
                color = (0, 255, 255)

            else:

                text = f"[ ] {name}"
                color = (255, 255, 255)

            draw_text(
                display,
                text,
                (20,70+i*30),
                color,
                0.65,
                2
            )


        cv2.imshow(window_name, display)

        
        cv2.waitKey(1)

        if len(clicked_points) == len(point_names):
            break
        
    cv2.destroyWindow(window_name)

    return clicked_points

# =====================================
# Select Video
# =====================================

def select_video():

    root = Tk()

    root.withdraw()

    root.attributes("-topmost", True)

    video_path = filedialog.askopenfilename(

        title="Select Video",

        filetypes=[

            ("Video Files", "*.mp4 *.avi *.mov *.mkv"),

            ("All Files", "*.*")

        ]

    )

    root.destroy()

    return video_path

# =====================================
# Ask Distance
# =====================================

def ask_real_distance():

    root = Tk()

    root.withdraw()

    root.attributes("-topmost", True)

    distance = simpledialog.askfloat(

        "Calibration",

        "Enter real distance (meters):",

        minvalue=0.01

    )

    root.destroy()

    return distance



# =====================================
# Main
# =====================================

video_path = select_video()

if video_path == "":

    print("No video selected.")

    exit()

cap = cv2.VideoCapture(video_path)

ret, frame = cap.read()

cap.release()

if not ret:
    print("Failed to load video.")
    exit()

print("\n==============================")
print("ROAD CALIBRATION")
print("==============================")

print(
    "\nChoose 4 road points in this order:\n"
    "1) Top Left\n"
    "2) Top Right\n"
    "3) Bottom Left\n"
    "4) Bottom Right\n"
)

road_points = select_points(
    frame,
    "ROAD CALIBRATION",
    [
        "Top Left",
        "Top Right",
        "Bottom Left",
        "Bottom Right"
    ]
)

print("\n==============================")
print("DISTANCE CALIBRATION")
print("==============================")

print(
    "\nChoose 2 points whose real distance is known"
)

distance_points = select_points(
    frame,
    "DISTANCE CALIBRATION",
    [
        "Point 1",
        "Point 2"
    ]
)

real_distance = ask_real_distance()

if real_distance is None:

    print("Calibration cancelled.")

    exit()

# =====================================
# Meter Per Pixel
# =====================================

x1, y1 = distance_points[0]
x2, y2 = distance_points[1]

pixel_distance = math.sqrt(
    (x2 - x1) ** 2 +
    (y2 - y1) ** 2
)

meter_per_pixel = (
    real_distance /
    pixel_distance
)

# =====================================
# Save JSON
# =====================================

data = {

    "video_path": video_path,

    "road_points": road_points,

    "distance_points": distance_points,

    "real_distance": real_distance,

    "pixel_distance": pixel_distance,

    "meter_per_pixel": meter_per_pixel
}

configs_dir = resource_path("configs")

os.makedirs(
    configs_dir,
    exist_ok=True
)

with open(
    resource_path("configs/calibration.json"),
    "w"
) as f:

    json.dump(
        data,
        f,
        indent=4
    )

root = Tk()

root.withdraw()

root.attributes("-topmost", True)

messagebox.showinfo(

    "Calibration Saved",

    f"Calibration completed successfully.\n\n"

    f"Pixel Distance : {pixel_distance:.2f}\n"

    f"Meter / Pixel : {meter_per_pixel:.6f}"

)

root.destroy()