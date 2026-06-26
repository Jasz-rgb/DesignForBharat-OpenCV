# 🏓 Table Tennis Ball Tracking & Haptic Feedback System

## Team Nirmaan51

A computer vision–based assistive prototype designed to improve the table tennis experience for visually impaired players. The system detects and tracks an orange table tennis ball from a recorded match, maps its position to real-world table coordinates using homography, detects bounce events through trajectory analysis, and can communicate the detected coordinates to an ESP32-based haptic feedback module. The current prototype demonstrates the computer vision pipeline and a proof-of-concept haptic feedback system using a vibration motor array.

<img width="1918" height="995" alt="image" src="https://github.com/user-attachments/assets/f2215385-aa94-4363-93e8-9b3ae53ec2e9" />

# 📌 Overview
This project processes a recorded table tennis match video and:
* Detects an orange table tennis ball using manually tuned HSV color thresholds.
* Suppresses the green table surface using HSV masking to reduce background interference.
* Tracks the ball position frame-by-frame using contour detection.
* Maps image coordinates to real-world table coordinates using homography.
* Detects bounce events from changes in the ball's vertical velocity.
* Generates an annotated output video.
* Logs detected bounce coordinates to a CSV file.
* Supports optional serial communication for an ESP32-based haptic feedback system.

# 🎯 Features
* 🎥 HSV-based ball detection for an orange table tennis ball.
* 🟩 Green table suppression using color masking.
* 🧹 Morphological filtering for noise reduction.
* ⚪ Contour-based ball localization.
* 📐 Homography-based coordinate transformation.
* 🟦 Velocity-based bounce detection.
* 📊 Automatic CSV logging of detected bounce coordinates.
* 💾 Annotated output video generation.
* 📡 Optional ESP32 serial communication for haptic feedback.

# 🛠️ Tech Stack
* Python 3.x
* OpenCV
* NumPy
* PySerial (optional)

# 📂 Project Structure
```text
DesignForBharat-OpenCV/
│
├── low_input.mp4
├── processed_output.mp4
├── ball_events.csv
├── table_corners.npy
├── calibrate_table.py
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

# 🚀 How to Use
## 🔹 Option 1: View Demo Output
Open:
```text
processed_output.mp4
```
to view the processed output showing:
* Ball tracking
* Bounce detection
* Coordinate annotations
* Frame counter
No installation is required.

## 🔹 Option 2: Run the Project
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Jasz-rgb/DesignForBharat-OpenCV.git
cd DesignForBharat-OpenCV
```

### 2️⃣ Create a Virtual Environment (Recommended)
```bash
python -m venv venv
```

Windows
```bash
venv\Scripts\activate
```

Linux / macOS
```bash
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

Example requirements:
```text
opencv-python>=4.8.0
numpy>=1.24
```

### 4️⃣ Recalibrate the Table
Run
```bash
python calibrate_table.py
```

Select the table corners in the following order:
1. Bottom Left
2. Bottom Right
3. Top Right
4. Top Left

A new calibration file (`table_corners.npy`) will be generated.

### 5️⃣ Run the Tracker
```bash
python main.py
```
Press **ESC** to exit.

# 📊 Outputs
## 🎥 Processed Video
`processed_output.mp4`

Contains:
* Ball tracking visualization
* Bounce detection
* Table coordinate annotations
* Frame counter
* Game Over indicator

## 📄 CSV Output
`ball_events.csv`

Contains:
* Frame number
* Table X coordinate (m)
* Table Y coordinate (m)

# 📐 Calibration
The project uses homography to convert image coordinates into real-world table coordinates.
Official table dimensions:
* **Length:** 2.74 m
* **Width:** 1.525 m

Calibration points are stored in:
```text
table_corners.npy
```

# 🧠 Processing Pipeline
For each frame:
1. Convert the frame from BGR to HSV.
2. Apply manually selected HSV thresholds to isolate the orange table tennis ball.
3. Remove the green table using a second HSV mask.
4. Apply morphological opening and closing to remove noise.
5. Detect contours and filter them by area and aspect ratio.
6. Compute the ball center.
7. Map the detected position to real-world table coordinates using homography.
8. Detect bounce events by identifying changes in the ball's vertical velocity.
9. Save detected bounce coordinates to a CSV file.
10. Generate the annotated output video.

# 📡 Optional Haptic Feedback Prototype
The project can be extended with an ESP32-based haptic feedback system. During processing, detected bounce coordinates may be transmitted via serial communication to an ESP32, which maps the received coordinates to a vibration motor array.
A sample hardware implementation is available on Tinkercad (implemented using an Arduino for simulation purposes):
https://www.tinkercad.com/things/6ncZs4p1ir9-nirmaan-51?sharecode=B983Z8PPOPA5wNuwnbbzW4-mVaB5TwioOyDHGHF5REA
> **Note:** The Tinkercad circuit demonstrates the hardware logic using an Arduino. The original prototype used an ESP32 to interface with the computer vision pipeline.

# 🚀 Future Improvements
* Improved bounce detection using trajectory smoothing.
* Automatic paddle hit detection.
* Deep learning-based ball detection.
* Live camera support.
* Multi-camera tracking.
* Smaller circuitry

# 👥 Developed By
**Team Nirmaan51**
