
# Face Authentication App

A simple desktop application for face authentication using your webcam. Built with Python, OpenCV, and Tkinter. Designed for educational and personal use on Windows.

---

## Features

- **Guided Live Enrollment:** Capture 5 images with different poses and expressions (neutral, smile, turn left/right, glasses on/off) for robust recognition.
- **Real-Time Authentication:** Uses your webcam to unlock the app by matching your live face to enrolled templates.
- **No Cloud, No Uploads:** All data is stored locally and securely.
- **Windows DPAPI Encryption:** Face templates are encrypted for privacy.
- **Easy to Use GUI:** Simple interface for enrollment and authentication.

---

## Setup

1. **Install Python 3.10+** (Windows recommended)
2. **Install dependencies:**
	 ```bash
	 pip install -r requirements.txt
	 ```
3. **Run the app:**
	 ```bash
	 python user_face_unlock.py
	 ```

---

## How It Works

1. **Enrollment:**
	 - On first run, the app will guide you to capture 5 live images:
		 1. Neutral face, looking straight
		 2. Smile
		 3. Turn head left
		 4. Turn head right
		 5. Remove/Put on glasses if you have
	 - The app extracts face features and saves them securely in:
		 ```
		 C:\Users\<your-username>\face_templates.dat
		 ```
2. **Authentication:**
	 - After enrollment, the app uses your webcam to authenticate you in real time.
	 - Recognition is robust to different conditions (lighting, pose, glasses).

---

## Usage

- **Start the app:**
	```bash
	python user_face_unlock.py
	```
- **Re-enroll:** Delete or rename `face_templates.dat` and run the app again.
- **Help:**
	```bash
	python user_face_unlock.py --help
	```

---

## Configuration

You can adjust these settings in `user_face_unlock.py`:

- `TOLERANCE` — Face matching threshold (default: 0.7)
- `LIVENESS_MATCHES_REQUIRED` — Number of matches needed to unlock (default: 3)
- `LIVENESS_WINDOW_SEC` — Time window for liveness detection (default: 5 seconds)

---

## Security & Privacy

- **Local Only:** No images or data are sent to the cloud.
- **Encrypted Storage:** Face templates are encrypted using Windows DPAPI.
- **No actual images are saved**—only processed face features.
- **For educational/personal use only.** Not a replacement for Windows login or critical security.

---

## Dependencies

- OpenCV (face detection)
- NumPy (numerical operations)
- Pillow (image processing)
- pywin32 (Windows DPAPI encryption)
- tkinter (GUI, included with Python)

---

## License

MIT License. See LICENSE file for details.
