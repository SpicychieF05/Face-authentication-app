

<p align="center">
	<img src="https://res.cloudinary.com/dlxybta5a/image/upload/v1757106882/limitless-banner_b5djgf.png" alt="LockLess Banner" width="100%" style="border-radius: 10px;"/>
</p>

<p align="center">
	<a href="https://github.com/SpicychieF05/Face-authentication-app" target="_blank">
		<img src="https://img.shields.io/github/forks/SpicychieF05/Face-authentication-app?style=social" alt="Forks">
	</a>
	<a href="https://github.com/SpicychieF05/Face-authentication-app" target="_blank">
		<img src="https://img.shields.io/github/watchers/SpicychieF05/Face-authentication-app?style=social" alt="Watchers">
	</a>
	<a href="https://github.com/SpicychieF05/Face-authentication-app" target="_blank">
		<img src="https://visitor-badge.laobi.icu/badge?page_id=SpicychieF05.Face-authentication-app" alt="Viewers">
	</a>
</p>

<p align="center">
	<a href="#setup"><img src="https://img.shields.io/badge/Setup-Guide-blue?style=for-the-badge" alt="Setup Guide"></a>
	<a href="#features"><img src="https://img.shields.io/badge/Features-List-green?style=for-the-badge" alt="Features"></a>
	<a href="#system-architecture-diagram"><img src="https://img.shields.io/badge/Diagram-Architecture-orange?style=for-the-badge" alt="Diagram"></a>
	<a href="#use-case-chart"><img src="https://img.shields.io/badge/Use%20Cases-Chart-yellow?style=for-the-badge" alt="Use Cases"></a>
</p>

# LockLess: Face Authentication App

LockLess is a secure desktop application for face authentication using your webcam. Built with Python, OpenCV, and Tkinter, it is designed for privacy, simplicity, and robust local security on Windows.


## Features


---

## System Architecture Diagram

```mermaid
flowchart TD
	User[User] -->|Enrolls Face| GUI[LockLess GUI]
	GUI -->|Captures Images| Webcam[Webcam]
	GUI -->|Saves Encrypted Templates| Storage[Local Storage]
	User -->|Authenticates| GUI
	GUI -->|Live Face Capture| Webcam
	GUI -->|Compares| Templates[Face Templates]
	Templates -->|Unlock| App[App Access]
```

---

## Use Case Chart

| Use Case                | Description                                                      | User Benefit                |
|-------------------------|------------------------------------------------------------------|-----------------------------|
| Secure Login            | Unlock app with your face, no password needed                    | Fast, hands-free access     |
| Local Data Protection   | All face data encrypted and stored locally                       | Privacy, no cloud risk      |
| Multi-Pose Enrollment   | Robust recognition with varied poses and expressions             | Reliable authentication     |
| Personal Device Unlock  | Use as a gatekeeper for sensitive files or apps                  | Extra layer of security     |
| Educational Demo        | Learn about face recognition and encryption                      | Knowledge, experimentation  |
| No Internet Required    | Works fully offline                                              | Usable anywhere             |

---

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

---

## 👨‍💻 **Developer Information**

### 🚀 **Built with ❤️ by Chirantan Mallick**
- 🎓 **BCA 3rd Year Student** at Seacom Skills University
- 💻 **Full Stack Developer** specializing in React & Modern Web Technologies
- 🌟 **Open Source Enthusiast** passionate about education technology

### 📞 **Connect with Developer**

<p align="center">
	<a href="https://discord.gg/EmRcW9rnGs">
		<img src="https://img.shields.io/badge/Discord-%237289DA.svg?style=plastic&logo=discord&logoColor=white" alt="Discord">
	</a>
	<a href="https://rb.gy/uxjdk">
		<img src="https://img.shields.io/badge/WhatsApp-25D366.svg?style=plastic&logo=whatsapp&logoColor=white" alt="WhatsApp">
	</a>
	<a href="https://www.facebook.com/Chirantan2965">
		<img src="https://img.shields.io/badge/Facebook-%231877F2.svg?style=plastic&logo=Facebook&logoColor=white" alt="Facebook">
	</a>
	<a href="https://instagram.com/heres_chirantan">
		<img src="https://img.shields.io/badge/Instagram-%23E4405F.svg?style=plastic&logo=Instagram&logoColor=white" alt="Instagram">
	</a>
	<a href="https://linkedin.com/in/chirantan-mallick">
		<img src="https://img.shields.io/badge/LinkedIn-%230077B5.svg?style=plastic&logo=linkedin&logoColor=white" alt="LinkedIn">
	</a>
	<a href="https://x.com/Chirantan2965">
		<img src="https://img.shields.io/badge/X-black.svg?style=plastic&logo=X&logoColor=white" alt="X">
	</a>
	<a href="https://tr.ee/9Vp509xCxy">
		<img src="https://img.shields.io/badge/Email-D14836.svg?style=plastic&logo=gmail&logoColor=white" alt="Email">
	</a>
</p>


	 - The app extracts face features and saves them securely in:
		 ```
		 C:\Users\<your-username>\face_templates.dat
		 ```
1. **Authentication:**
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
