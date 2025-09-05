#!/usr/bin/env python3
"""
Face Model Manager - Helper script to manage face enrollments
"""

import os
import sys
from user_face_unlock import enroll_from_image


def list_face_models():
    """List all available face model images"""
    face_model_dir = "face_model"
    if not os.path.exists(face_model_dir):
        print("❌ Face model directory not found!")
        return []

    images = []
    for file in os.listdir(face_model_dir):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
            images.append(file)

    return sorted(images)


def show_face_models():
    """Display all available face model images"""
    images = list_face_models()

    if not images:
        print("❌ No face model images found in face_model/ directory")
        return

    print(f"📸 Found {len(images)} face model images:")
    for i, image in enumerate(images, 1):
        print(f"  {i:2d}. {image}")


def enroll_by_number(image_number):
    """Enroll a face by image number"""
    images = list_face_models()

    if not images:
        print("❌ No face model images found!")
        return False

    if image_number < 1 or image_number > len(images):
        print(f"❌ Invalid image number. Please choose 1-{len(images)}")
        return False

    image_path = os.path.join("face_model", images[image_number - 1])
    print(f"🔄 Enrolling face from: {image_path}")

    success = enroll_from_image(image_path)
    if success:
        print("✅ Enrollment successful!")
        print("\nYou can now run the face unlock with:")
        print("python user_face_unlock.py")
    else:
        print("❌ Enrollment failed!")

    return success


def main():
    """Main function"""
    if len(sys.argv) == 1:
        print("Face Model Manager")
        print("==================")
        show_face_models()
        print("\nUsage:")
        print("  python face_model_manager.py list                    # List all images")
        print("  python face_model_manager.py enroll <number>         # Enroll by number")
        print("  python face_model_manager.py enroll <filename>       # Enroll by filename")
        print("\nExample:")
        print("  python face_model_manager.py enroll 1")
        print("  python face_model_manager.py enroll WIN_20250905_22_02_17_Pro.jpg")

    elif len(sys.argv) == 2 and sys.argv[1] == "list":
        show_face_models()

    elif len(sys.argv) == 3 and sys.argv[1] == "enroll":
        arg = sys.argv[2]

        # Check if it's a number
        try:
            image_number = int(arg)
            enroll_by_number(image_number)
        except ValueError:
            # It's a filename
            image_path = os.path.join("face_model", arg)
            if os.path.exists(image_path):
                print(f"🔄 Enrolling face from: {image_path}")
                success = enroll_from_image(image_path)
                if success:
                    print("✅ Enrollment successful!")
                else:
                    print("❌ Enrollment failed!")
            else:
                print(f"❌ Image file not found: {image_path}")
    else:
        print("❌ Invalid arguments. Run without arguments to see usage.")


if __name__ == "__main__":
    main()
