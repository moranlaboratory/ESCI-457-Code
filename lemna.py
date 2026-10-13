from picamera2 import Picamera2
import cv2
import os

# === USER SETTINGS ===
output_dir = "/home/huxpi/captured_images"  # Update as needed
image_prefix = "img_"
image_extension = ".jpg"  # Make sure this starts with a dot

# === Ensure output directory exists ===
os.makedirs(output_dir, exist_ok=True)

# === Determine next available index ===
def get_next_index(directory, prefix, extension):
    indices = []
    for filename in os.listdir(directory):
        if not filename.startswith(prefix) or not filename.endswith(extension):
            continue
        base = filename[len(prefix):-len(extension)]
        if base.isdigit():
            indices.append(int(base))
        else:
            print(f"Skipping non-numeric file: {filename}")
    return max(indices) + 1 if indices else 0

img_counter = get_next_index(output_dir, image_prefix, image_extension)

# === Start the camera ===
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

print("Preview started. Press 'c' to capture, 'q' to quit.")

# === Main loop ===
while True:
    frame = picam2.capture_array()
    cv2.imshow("Live Preview - Press 'c' to capture, 'q' to quit", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):
        filename = f"{image_prefix}{img_counter:04d}{image_extension}"
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, frame)
        print(f"Captured {filename}")
        img_counter += 1

    elif key == ord('q'):
        print("Exiting...")
        break

# === Cleanup ===
cv2.destroyAllWindows()
picam2.close()
