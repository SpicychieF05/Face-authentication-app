# Face Unlock System

A simple face authentication system for educational purposes using OpenCV.

## Features
- Face enrollment from images
- Real-time face recognition via webcam
- Windows DPAPI encryption for face templates
- Liveness detection with multiple frame matching
- Robust error handling

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Enroll Your Face
```bash
python user_face_unlock.py enroll face_model/your_image.jpg
```

### 3. Run Face Unlock
```bash
python user_face_unlock.py
```

## Usage

### Basic Commands
- `python user_face_unlock.py --help` - Show help
- `python user_face_unlock.py enroll <image_path>` - Enroll face from image
- `python user_face_unlock.py` - Run face unlock system

### Face Model Manager (Optional)
- `python face_model_manager.py` - List all available face images
- `python face_model_manager.py enroll 1` - Enroll by image number
- `python face_model_manager.py enroll filename.jpg` - Enroll by filename

## Configuration
Edit these constants in `user_face_unlock.py`:
- `TOLERANCE` - Face matching threshold (0.7 = 70% similarity required)
- `LIVENESS_MATCHES_REQUIRED` - Number of successful matches needed (default: 3)
- `LIVENESS_WINDOW_SEC` - Time window for liveness detection (default: 5 seconds)

## Security Note
This is for educational purposes only. Do NOT use as a replacement for Windows login or critical security systems.

## Dependencies
- OpenCV (face detection)
- NumPy (numerical operations)
- Pillow (image processing)
- pywin32 (Windows DPAPI encryption)
- tkinter (GUI - included with Python)
