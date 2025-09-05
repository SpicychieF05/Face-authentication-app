import os
import sys
import time
import logging
import threading
from typing import Optional, Tuple, List
import cv2
import pickle
import numpy as np
try:
    import win32crypt
    CryptProtectData = win32crypt.CryptProtectData
    CryptUnprotectData = win32crypt.CryptUnprotectData
except ImportError:
    # pywin32 not installed or not on Windows
    def CryptProtectData(data, *args, **kwargs):
        return data

    def CryptUnprotectData(data, *args, **kwargs):
        return (None, data)
from tkinter import Tk, Label, Button, messagebox
from PIL import Image, ImageTk

# Configuration
TEMPLATE_FILE = os.path.expanduser(r"~\face_templates.dat")
TOLERANCE = 0.7  # for OpenCV template matching (0.0 to 1.0, higher = stricter)
CAMERA_INDEX = 0
FRAME_SKIP = 2  # Process every nth frame for performance
MIN_FACE_SIZE = (50, 50)  # Minimum face size to consider
LIVENESS_MATCHES_REQUIRED = 3
LIVENESS_WINDOW_SEC = 5
RECOGNITION_INTERVAL_MS = 1000

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize OpenCV face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def extract_face_features(face_img: np.ndarray) -> np.ndarray:
    """Extract simple features from a face image for comparison"""
    # Resize to standard size
    face_img = cv2.resize(face_img, (64, 64))
    # Convert to grayscale if needed
    if len(face_img.shape) == 3:
        face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    # Normalize
    face_img = cv2.equalizeHist(face_img)
    # Flatten to feature vector
    return face_img.flatten().astype(np.float32) / 255.0


def compare_faces(features1: np.ndarray, features2: np.ndarray) -> float:
    """Compare two face feature vectors and return similarity score (0-1, higher = more similar)"""
    # Use normalized correlation
    correlation = np.corrcoef(features1, features2)[0, 1]
    # Handle NaN case
    if np.isnan(correlation):
        return 0.0
    return max(0.0, correlation)  # Ensure non-negative


def dpapi_protect(data_bytes: bytes) -> bytes:
    """Encrypt data using Windows DPAPI"""
    try:
        blob = CryptProtectData(data_bytes, None, None, None, None, 0)
        return blob
    except Exception as e:
        logging.warning(f"DPAPI protection failed, using fallback: {e}")
        return data_bytes


def dpapi_unprotect(blob: bytes) -> bytes:
    """Decrypt data using Windows DPAPI"""
    try:
        result = CryptUnprotectData(blob, None, None, None, 0)
        return result[1] if isinstance(result, tuple) else blob
    except Exception as e:
        logging.warning(f"DPAPI unprotection failed, using fallback: {e}")
        return blob


def validate_image_path(img_path: str) -> bool:
    """Validate if image path exists and is a valid image file"""
    if not os.path.exists(img_path):
        logging.error(f"Image file not found: {img_path}")
        return False

    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    if not img_path.lower().endswith(valid_extensions):
        logging.error(f"Invalid image format. Supported: {valid_extensions}")
        return False

    return True


def enroll_all_images_in_folder(folder: str = "face_model") -> bool:
    """Enroll faces from all images in the folder and save all templates"""
    templates = []
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    if not os.path.exists(folder):
        logging.error(f"Face model folder not found: {folder}")
        return False
    image_files = [f for f in os.listdir(
        folder) if f.lower().endswith(valid_extensions)]
    if not image_files:
        logging.error("No valid images found in face_model folder")
        return False
    for img_file in image_files:
        img_path = os.path.join(folder, img_file)
        logging.info(f"Processing image: {img_path}")
        img = cv2.imread(img_path)
        if img is None:
            logging.warning(f"Failed to load image: {img_path}")
            continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=MIN_FACE_SIZE
        )
        if len(faces) == 0:
            logging.warning(f"No face found in image: {img_path}")
            continue
        # Use largest face
        face_areas = [w * h for (x, y, w, h) in faces]
        largest_face_idx = np.argmax(face_areas)
        x, y, w, h = faces[largest_face_idx]
        face_img = gray[y:y+h, x:x+w]
        features = extract_face_features(face_img)
        templates.append(features)
    if not templates:
        logging.error("No faces enrolled from images.")
        return False
    # Save all templates
    data = pickle.dumps(templates)
    protected = dpapi_protect(data)
    with open(TEMPLATE_FILE, "wb") as f:
        f.write(protected)
    logging.info(
        f"Enrolled {len(templates)} face templates from {len(image_files)} images.")
    return True


def load_templates() -> Optional[List[np.ndarray]]:
    """Load all enrolled face templates"""
    try:
        if not os.path.exists(TEMPLATE_FILE):
            logging.warning("No face templates found")
            return None
        with open(TEMPLATE_FILE, "rb") as f:
            blob = f.read()
        data = dpapi_unprotect(blob)
        templates = pickle.loads(data)
        logging.info(f"Loaded {len(templates)} face templates")
        return templates
    except Exception as e:
        logging.error(f"Failed to load templates: {e}")
        return None


class CameraManager:
    """Improved camera management with proper resource handling"""

    def __init__(self, camera_index: int = CAMERA_INDEX):
        self.camera_index = camera_index
        self.cap = None
        self.is_initialized = False

    def initialize(self) -> bool:
        """Initialize camera with optimized settings"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)

            if not self.cap.isOpened():
                logging.error(f"Failed to open camera {self.camera_index}")
                return False

            # Optimize camera settings for performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            # Reduce buffer to get latest frame
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            self.is_initialized = True
            logging.info(
                f"Camera {self.camera_index} initialized successfully")
            return True

        except Exception as e:
            logging.error(f"Camera initialization failed: {e}")
            return False

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read a frame from the camera"""
        if not self.is_initialized or self.cap is None:
            return False, None

        ret, frame = self.cap.read()
        return ret, frame

    def release(self):
        """Properly release camera resources"""
        try:
            if self.cap is not None:
                self.cap.release()
                self.is_initialized = False
                logging.info("Camera released")
        except Exception as e:
            logging.error(f"Error releasing camera: {e}")

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

# Optimized liveness detection with better performance and security


def is_live_sequence(matches_required: int = LIVENESS_MATCHES_REQUIRED,
                     window_sec: int = LIVENESS_WINDOW_SEC) -> bool:
    """
    Enhanced liveness detection with frame skipping and better face validation
    """
    templates = load_templates()
    if not templates:
        logging.error("No templates available for recognition")
        return False

    with CameraManager() as camera:
        if not camera.is_initialized:
            logging.error("Failed to initialize camera for liveness detection")
            return False

        matches = 0
        start_time = time.time()
        frame_count = 0
        valid_detections = 0

        logging.info(
            f"Starting liveness detection (need {matches_required} matches in {window_sec}s)")

        while time.time() - start_time < window_sec and matches < matches_required:
            ret, frame = camera.read_frame()
            if not ret or frame is None:
                continue

            frame_count += 1

            # Skip frames for performance (process every nth frame)
            if frame_count % FRAME_SKIP != 0:
                continue

            try:
                # Convert to grayscale for face detection
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detect faces using OpenCV
                faces = face_cascade.detectMultiScale(
                    gray_frame,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=MIN_FACE_SIZE
                )

                if len(faces) == 0:
                    continue

                valid_detections += 1

                # Process each detected face
                for (x, y, w, h) in faces:
                    # Extract face region
                    face_img = gray_frame[y:y+h, x:x+w]

                    # Extract features
                    features = extract_face_features(face_img)

                    # Compare with all templates
                    for idx, template in enumerate(templates):
                        similarity = compare_faces(template, features)
                        if similarity >= TOLERANCE:
                            matches += 1
                            logging.info(
                                f"Face match {matches}/{matches_required} (template {idx+1}, similarity: {similarity:.3f})")
                            break

            except Exception as e:
                logging.error(f"Error during face recognition: {e}")
                continue

        elapsed_time = time.time() - start_time
        logging.info(f"Liveness check completed: {matches}/{matches_required} matches, "
                     f"{valid_detections} valid detections in {elapsed_time:.1f}s")

        return matches >= matches_required

# Enhanced GUI lock screen with better user experience


class GuidedEnrollment:
    """Guided live enrollment for capturing 5 images with instructions"""
    INSTRUCTIONS = [
        "1. Neutral face, looking straight",
        "2. Smile",
        "3. Turn head left",
        "4. Turn head right",
        "5. Remove/Put on glasses if you have"
    ]

    def __init__(self, root):
        self.root = root
        self.current_step = 0
        self.captured_images = []
        self.camera = CameraManager()
        self.frame = None
        self.is_camera_ready = self.camera.initialize()

        root.title("Guided Face Enrollment")
        root.geometry("800x600")
        root.configure(bg="black")

        self.instruction_label = Label(
            root, text=self.INSTRUCTIONS[0], fg="white", bg="black", font=("Segoe UI", 20))
        self.instruction_label.pack(pady=20)

        self.image_panel = Label(root, bg="black")
        self.image_panel.pack(pady=10)

        self.capture_btn = Button(root, text="Capture", command=self.capture_image, font=(
            "Segoe UI", 14), bg="green", fg="white")
        self.capture_btn.pack(pady=10)

        self.next_btn = Button(root, text="Next", command=self.next_step, font=(
            "Segoe UI", 14), bg="blue", fg="white", state="disabled")
        self.next_btn.pack(pady=10)

        self.status_label = Label(
            root, text="", fg="yellow", bg="black", font=("Segoe UI", 12))
        self.status_label.pack(pady=10)

        self.update_camera()

    def update_camera(self):
        if not self.is_camera_ready:
            self.status_label.config(text="Camera not available!")
            return
        ret, frame = self.camera.read_frame()
        if ret and frame is not None:
            self.frame = frame
            # Convert to PIL image for Tkinter
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            img = img.resize((400, 300))
            imgtk = ImageTk.PhotoImage(image=img)
            self.image_panel.imgtk = imgtk
            self.image_panel.config(image=imgtk)
        self.root.after(50, self.update_camera)

    def capture_image(self):
        if self.frame is not None:
            self.captured_images.append(self.frame.copy())
            self.status_label.config(
                text=f"Captured image {self.current_step+1}/5")
            self.capture_btn.config(state="disabled")
            self.next_btn.config(state="normal")

    def next_step(self):
        self.current_step += 1
        if self.current_step < len(self.INSTRUCTIONS):
            self.instruction_label.config(
                text=self.INSTRUCTIONS[self.current_step])
            self.capture_btn.config(state="normal")
            self.next_btn.config(state="disabled")
            self.status_label.config(text="")
        else:
            self.finish_enrollment()

    def finish_enrollment(self):
        self.status_label.config(text="Processing images...")
        self.root.update()
        templates = []
        for idx, img in enumerate(self.captured_images):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=MIN_FACE_SIZE
            )
            if len(faces) == 0:
                self.status_label.config(
                    text=f"No face detected in image {idx+1}")
                continue
            face_areas = [w * h for (x, y, w, h) in faces]
            largest_face_idx = np.argmax(face_areas)
            x, y, w, h = faces[largest_face_idx]
            face_img = gray[y:y+h, x:x+w]
            features = extract_face_features(face_img)
            templates.append(features)
        if not templates:
            self.status_label.config(
                text="No valid faces captured. Please try again.")
            return
        # Save all templates
        data = pickle.dumps(templates)
        protected = dpapi_protect(data)
        with open(TEMPLATE_FILE, "wb") as f:
            f.write(protected)
        self.status_label.config(
            text=f"Enrollment complete! {len(templates)} images saved.")
        self.camera.release()
        self.root.after(1500, self.root.destroy)


class LockScreen:
    """Improved lock screen with better threading and user feedback"""

    def __init__(self, root):
        self.root = root
        self.is_checking = False
        self.check_thread = None

        # Configure window
        root.attributes("-fullscreen", True)
        root.configure(bg="black")
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Status label
        self.status_label = Label(
            root,
            text="🔒 System Locked",
            fg="white",
            bg="black",
            font=("Segoe UI", 32, "bold")
        )
        self.status_label.pack(pady=(100, 20))

        # Main label
        self.main_label = Label(
            root,
            text="Looking for authorized user...",
            fg="lightblue",
            bg="black",
            font=("Segoe UI", 18)
        )
        self.main_label.pack(pady=20)

        # Progress indicator
        self.progress_label = Label(
            root,
            text="●○○",
            fg="yellow",
            bg="black",
            font=("Segoe UI", 24)
        )
        self.progress_label.pack(pady=10)

        # Admin exit button (for development)
        self.exit_btn = Button(
            root,
            text="Exit (Development Only)",
            command=self.admin_exit,
            bg="darkred",
            fg="white",
            font=("Segoe UI", 10)
        )
        self.exit_btn.pack(side="bottom", pady=20)

        # Start recognition after a short delay
        root.after(1000, self.start_recognition)

    def update_progress(self, dots="●○○"):
        """Update progress indicator"""
        self.progress_label.config(text=dots)

    def update_status(self, message: str, color: str = "lightblue"):
        """Update status message"""
        self.main_label.config(text=message, fg=color)

    def start_recognition(self):
        """Start face recognition in a separate thread"""
        if not self.is_checking:
            self.is_checking = True
            self.check_thread = threading.Thread(
                target=self.recognition_worker, daemon=True)
            self.check_thread.start()

    def recognition_worker(self):
        """Worker thread for face recognition"""
        try:
            self.root.after(0, lambda: self.update_status(
                "Initializing camera...", "yellow"))
            self.root.after(0, lambda: self.update_progress("●●○"))

            if is_live_sequence():
                self.root.after(0, lambda: self.update_status(
                    "✓ Face recognized! Unlocking...", "lightgreen"))
                self.root.after(0, lambda: self.update_progress("●●●"))
                self.root.after(1000, self.unlock_system)
            else:
                self.root.after(0, lambda: self.update_status(
                    "❌ Recognition failed. Retrying...", "orange"))
                self.root.after(0, lambda: self.update_progress("●○○"))
                self.is_checking = False
                self.root.after(RECOGNITION_INTERVAL_MS,
                                self.start_recognition)

        except Exception as e:
            logging.error(f"Recognition worker error: {e}")
            self.root.after(0, lambda: self.update_status(
                "⚠ Error occurred. Retrying...", "red"))
            self.is_checking = False
            self.root.after(RECOGNITION_INTERVAL_MS *
                            2, self.start_recognition)

    def unlock_system(self):
        """Unlock the system"""
        logging.info("User authenticated successfully")
        messagebox.showinfo("Face Unlock", "Authentication successful!")
        self.root.destroy()

    def admin_exit(self):
        """Administrative exit for development"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit? (Development only)"):
            logging.info("Administrative exit")
            self.root.destroy()
            sys.exit(0)

    def on_closing(self):
        """Handle window closing"""
        # Prevent normal closing in lock mode
        pass


def main():
    """Enhanced main function with better error handling and user guidance"""
    # Check for enrollment command
    if len(sys.argv) >= 2 and sys.argv[1] == "enroll":
        print("Enrolling faces from all images in face_model/ ...")
        if enroll_all_images_in_folder("face_model"):
            print(f"✓ Enrollment successful! {TEMPLATE_FILE} updated.")
            print("You can now run the face unlock with:")
            print(f"python {sys.argv[0]}")
        else:
            print("❌ Enrollment failed!")
        return

    # Check for help command
    if len(sys.argv) >= 2 and sys.argv[1] in ["-h", "--help", "help"]:
        print("Face Unlock System - Usage:")
        print(f"  Enroll:  python {sys.argv[0]} enroll <image_path>")
        print(f"  Unlock:  python {sys.argv[0]}")
        print(f"\nExample enrollment:")
        print(f"  python {sys.argv[0]} enroll face_model/your_photo.jpg")
        print(f"\nConfiguration:")
        print(f"  Tolerance: {TOLERANCE} (lower = stricter)")
        print(f"  Template file: {TEMPLATE_FILE}")
        return

    try:
        # Always run guided enrollment before authentication
        print("Starting guided enrollment...")
        root = Tk()
        GuidedEnrollment(root)
        root.mainloop()
        print("Enrollment finished. Starting face authentication...")

        # Verify templates are valid
        templates = load_templates()
        if not templates:
            print("❌ Failed to load face templates!")
            print("The template file may be corrupted. Please re-enroll:")
            print(f"python {sys.argv[0]} enroll")
            return

        print("🔒 Starting Face Unlock System...")
        print("Press Ctrl+C to exit or use the development exit button")

        # Initialize GUI
        root = Tk()
        root.title("Face Unlock System")

        app = LockScreen(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("\n⚠ Program interrupted by user")
    except Exception as e:
        logging.error(f"Main function error: {e}")
        print(f"❌ An error occurred: {e}")
        print("Please check the logs for more details.")


if __name__ == "__main__":
    main()
