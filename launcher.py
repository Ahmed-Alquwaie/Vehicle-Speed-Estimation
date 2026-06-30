import os
import json
import customtkinter as ctk
import subprocess
import sys

# ==========================
# Resource Path
# ==========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    return os.path.join(BASE_DIR, relative_path)

# ==========================
# App Settings
# ==========================

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = resource_path("configs/calibration.json")

# ==========================
# Window
# ==========================

app = ctk.CTk()

app.title("Vehicle Speed Estimation")

app.geometry("700x450")

app.resizable(False, False)

# ==========================
# Title
# ==========================

title = ctk.CTkLabel(
    app,
    text="Vehicle Speed Estimation",
    font=("Segoe UI", 28, "bold")
)

title.pack(pady=20)

# ==========================
# Info Frame
# ==========================

info_frame = ctk.CTkFrame(app)

info_frame.pack(fill="x", padx=30)

video_label = ctk.CTkLabel(
    info_frame,
    text="Video : No video selected",
    anchor="w",
    font=("Segoe UI", 15)
)

video_label.pack(anchor="w", padx=15, pady=(15,5))

status_label = ctk.CTkLabel(
    info_frame,
    text="Calibration : Not Found",
    anchor="w",
    font=("Segoe UI", 15)
)

status_label.pack(anchor="w", padx=15, pady=(0,15))

# ==========================
# Read Calibration
# ==========================

def refresh_status():

    if os.path.exists(CONFIG_FILE):

        try:

            with open(CONFIG_FILE, "r") as f:

                data = json.load(f)

            video = os.path.basename(data["video_path"])

            video_label.configure(
                text=f"Video : {video}"
            )

            status_label.configure(
                text="Calibration : Found ✅"
            )

        except:

            status_label.configure(
                text="Calibration : Invalid ❌"
            )

    else:

        video_label.configure(
            text="Video : No video selected"
        )

        status_label.configure(
            text="Calibration : Not Found ❌"
        )

refresh_status()

def run_calibration():

    app.withdraw()

    subprocess.run([sys.executable, "calibration.py"])

    app.deiconify()

    refresh_status()
    
def run_speed_estimation():

    app.withdraw()

    subprocess.run([sys.executable, "speed_estimation.py"])

    app.deiconify()
# ==========================
# Buttons
# ==========================

button_frame = ctk.CTkFrame(app)

button_frame.pack(pady=35)

calibration_btn = ctk.CTkButton(
    button_frame,
    text="Start Calibration",
    width=250,
    height=45,
    command=run_calibration
)

calibration_btn.pack(pady=10)

speed_btn = ctk.CTkButton(
    button_frame,
    text="Start Speed Estimation",
    width=250,
    height=45,
    command=run_speed_estimation
)

speed_btn.pack(pady=10)

# ==========================
# Footer
# ==========================

footer = ctk.CTkLabel(
    app,
    text="Version 1.0",
    text_color="gray"
)

footer.pack(side="bottom", pady=15)

app.mainloop()
