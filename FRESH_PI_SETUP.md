# Fresh Raspberry Pi setup for `lemna.py` (Arducam IMX519)

Audience: someone who has not set up a Raspberry Pi before.  
Goal: boot a fresh **Raspberry Pi OS (Desktop)** image and run `lemna.py` with an **Arducam IMX519** camera.

You will use the **Terminal** app on the Pi desktop for almost every step. Open it with: menu → **Accessories** → **Terminal**, or press `Ctrl+Alt+T`.

---

## Before you start (parts checklist)

- Raspberry Pi (4 or 5 recommended)
- MicroSD card (16 GB+)
- Power supply for the Pi
- Monitor + HDMI cable, keyboard, mouse (needed for the live preview window)
- Arducam IMX519 camera + CSI ribbon cable
- USB stick or network access so you can copy `lemna.py` onto the Pi  
  (this guide lives next to `lemna.py` in the `ESCI457_CameraGUI` folder on the MORAN_2 USB)

**Username note:** `lemna.py` saves images to `/home/huxpi/captured_images`. That matches the lab username `huxpi`. If your Pi account is different (for example `pi`), either create that path carefully or edit the script — see Step 9.

---

## Step 1 — Flash Raspberry Pi OS and first boot

1. On another computer, download **Raspberry Pi Imager**: https://www.raspberrypi.com/software/
2. Insert the microSD card.
3. Open Imager and choose:
   - **Raspberry Pi Device** — your Pi model
   - **Operating System** — **Raspberry Pi OS (64-bit)** with **Desktop** (not Lite)
   - **Storage** — your microSD card
4. Click the gear / **OS customisation** (if offered) and set:
   - hostname (optional)
   - username / password — use **`huxpi`** if you want the script’s default path to work unchanged
   - Wi‑Fi (if needed)
   - Enable SSH only if you want it (not required for this guide)
5. Write the image, eject the card, insert it into the Pi, connect monitor/keyboard/mouse, and power on.
6. Finish the first-boot wizard (timezone, updates if offered). Log in to the desktop.

---

## Step 2 — Update the system

Open Terminal and run these commands one at a time (press Enter after each; wait for each to finish):

```bash
sudo apt update
```

```bash
sudo apt full-upgrade -y
```

If the upgrade installed a new kernel, reboot:

```bash
sudo reboot
```

After reboot, open Terminal again.

---

## Step 3 — Connect the Arducam IMX519 (power OFF first)

**Important: shut the Pi down and unplug power before plugging in the camera.**

```bash
sudo shutdown -h now
```

Wait until the green activity LED stops blinking, then unplug the power cable.

1. Lift the CSI connector latch on the Pi (usually the black plastic bar on the camera port).
2. Insert the ribbon with the contacts facing the correct way for your Pi model (contacts toward the HDMI ports on many Pi 4 boards — check Arducam’s diagram for your Pi).
3. Push the latch closed so the ribbon is firm and straight.
4. Plug power back in and boot to the desktop. Open Terminal.

---

## Step 4 — Configure the camera in `/boot/firmware/config.txt`

Raspberry Pi OS Bookworm/Trixie stores boot settings here:

`/boot/firmware/config.txt`

### Option A — Edit with nano (easiest to follow)

Open the file:

```bash
sudo nano /boot/firmware/config.txt
```

1. Use the arrow keys to scroll. Look for a line like:
   ```
   camera_auto_detect=1
   ```
   Change it to:
   ```
   camera_auto_detect=0
   ```
   If that line does not exist, you will add it in the next part.

2. Scroll to the **bottom** of the file. Add these two lines on their own (if they are not already there):

```
camera_auto_detect=0
dtoverlay=imx519
```

3. Save and exit nano:
   - Press **`Ctrl+O`** (write Out), then **Enter** to confirm the filename
   - Press **`Ctrl+X`** to exit

4. Confirm the lines are present:

```bash
grep -E 'camera_auto_detect|imx519' /boot/firmware/config.txt
```

You should see `camera_auto_detect=0` and `dtoverlay=imx519`.

### Option B — Copy-paste append (no interactive editor)

If you prefer not to use nano, run:

```bash
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.bak
```

```bash
sudo sed -i 's/^camera_auto_detect=1/camera_auto_detect=0/' /boot/firmware/config.txt
```

```bash
grep -q '^camera_auto_detect=' /boot/firmware/config.txt || echo 'camera_auto_detect=0' | sudo tee -a /boot/firmware/config.txt
```

```bash
grep -q '^dtoverlay=imx519' /boot/firmware/config.txt || echo 'dtoverlay=imx519' | sudo tee -a /boot/firmware/config.txt
```

```bash
grep -E 'camera_auto_detect|imx519' /boot/firmware/config.txt
```

**Note:** Some Arducam IMX519 SKUs (especially autofocus / Pivariety) document a slightly different overlay. If the camera is not detected after Step 7, check Arducam’s current IMX519 guide for your exact module and replace `dtoverlay=imx519` with what they specify.

Do **not** reboot yet — install Arducam packages first (next step), then reboot once.

---

## Step 5 — Install Arducam Pivariety / libcamera packages

Many IMX519 modules need Arducam’s libcamera packages instead of (or in addition to) the stock Raspberry Pi ones.

### 5a — See which Debian release you are on

```bash
cat /etc/os-release | grep VERSION_CODENAME
```

Remember the codename. Common values:

- `bookworm`
- `trixie`

### 5b — Download Arducam’s installer

```bash
cd ~
```

```bash
wget -O install_pivariety_pkgs.sh \
  https://github.com/ArduCAM/Arducam-Pivariety-V4L2-Driver/releases/download/install_script/install_pivariety_pkgs.sh
```

```bash
chmod +x install_pivariety_pkgs.sh
```

### 5c — Install packages for your codename

**If your codename is `bookworm`:**

```bash
./install_pivariety_pkgs.sh -p libcamera_bookworm
```

```bash
./install_pivariety_pkgs.sh -p libcamera_apps_bookworm
```

**If your codename is `trixie`:**

```bash
./install_pivariety_pkgs.sh -p libcamera_trixie
```

```bash
./install_pivariety_pkgs.sh -p libcamera_apps_trixie
```

**If you are unsure**, try auto-detect:

```bash
./install_pivariety_pkgs.sh -d
```

If the script errors (for example about `raspberrypi-kernel` / version compare), note the error text. You can still try the reboot + verify steps; some Pi OS versions detect IMX519 with only the overlay. Follow Arducam’s current docs if verify fails.

---

## Step 6 — Reboot

```bash
sudo reboot
```

Log back into the desktop and open Terminal.

---

## Step 7 — Verify the camera

Try the modern tool first:

```bash
rpicam-hello -t 3000
```

You should see a short camera preview for about 3 seconds.

If `rpicam-hello` is not found, try:

```bash
libcamera-hello -t 3000
```

Optional still test:

```bash
rpicam-still -o ~/test_imx519.jpg
```

```bash
ls -la ~/test_imx519.jpg
```

If these commands fail, jump to **Troubleshooting** at the end before continuing.

---

## Step 8 — Install Python packages for `lemna.py`

```bash
sudo apt update
```

```bash
sudo apt install -y python3-picamera2 python3-opencv
```

Quick import check:

```bash
python3 -c "from picamera2 import Picamera2; import cv2; print('OK: picamera2 and cv2 import')"
```

---

## Step 9 — Create the image output folder

`lemna.py` writes to `/home/huxpi/captured_images` by default.

**If your username is `huxpi`:**

```bash
mkdir -p /home/huxpi/captured_images
```

```bash
ls -ld /home/huxpi/captured_images
```

**If your username is something else** (check with `whoami`):

```bash
whoami
```

```bash
echo $HOME
```

Either:

1. Create the lab path only if you understand permissions (usually easier to edit the script), **or**
2. Edit `lemna.py` and change the line:
   ```python
   output_dir = "/home/huxpi/captured_images"
   ```
   to:
   ```python
   output_dir = "/home/YOUR_USERNAME/captured_images"
   ```
   Then:
   ```bash
   mkdir -p ~/captured_images
   ```

To edit with nano after you have a local copy of the script:

```bash
nano ~/lemna.py
```

Change `output_dir`, then `Ctrl+O`, Enter, `Ctrl+X`.

---

## Step 10 — Copy `lemna.py` onto the Pi

`lemna.py` is on the MORAN_2 USB in:

- `ESCI457_CameraGUI/lemna.py` (same folder as this guide)
- also `RISE Lemna 2025/lemna.py` (identical copy)

### If the USB is plugged into this Pi

1. Plug in the USB stick. It usually appears under `/media/` or on the desktop.
2. Find the mount path (example — yours may differ):

```bash
ls /media/$USER/
```

```bash
find /media/$USER -name 'lemna.py' 2>/dev/null
```

3. Copy it to your home folder (adjust the path to match `find` output):

```bash
cp "/media/$USER/MORAN_2/ESCI457_CameraGUI/lemna.py" ~/lemna.py
```

```bash
ls -la ~/lemna.py
```

### If you already have the file elsewhere

```bash
cp /path/to/lemna.py ~/lemna.py
```

---

## Step 11 — Run `lemna.py` on the desktop

**Must be run in a graphical desktop session** (not a plain SSH login without display forwarding). On the Pi desktop, open Terminal and run:

```bash
cd ~
```

```bash
python3 lemna.py
```

You should see:

- a window titled like **Live Preview - Press 'c' to capture, 'q' to quit**
- terminal text: `Preview started. Press 'c' to capture, 'q' to quit.`

### Keys

| Key | Action |
|-----|--------|
| **`c`** | Capture current frame → saves `img_0000.jpg`, `img_0001.jpg`, … |
| **`q`** | Quit and close the camera |

Click the preview window once so keyboard focus is on it, then press `c` / `q`.

### Confirm captures

```bash
ls -la /home/huxpi/captured_images/
```

(or `ls -la ~/captured_images/` if you changed `output_dir`)

---

## Done

You now have:

1. Updated Raspberry Pi OS Desktop  
2. IMX519 enabled in `config.txt`  
3. Arducam libcamera packages (when the installer succeeds)  
4. `python3-picamera2` and `python3-opencv`  
5. Working `lemna.py` still capture  

---

## Troubleshooting

### Preview window does not open / “cannot connect to X server” / headless

`lemna.py` uses OpenCV `imshow`, which needs a display.

- Run from the **Pi desktop** Terminal, not SSH.
- If using SSH from another machine, you need X11/Wayland forwarding and a local X server — easier to sit at the Pi instead.
- Confirm you installed **Desktop** OS, not Lite.

### Camera not detected (`rpicam-hello` / `libcamera-hello` errors)

1. Power off, reseat the CSI ribbon, power on.
2. Recheck config:
   ```bash
   grep -E 'camera_auto_detect|dtoverlay' /boot/firmware/config.txt
   ```
3. Confirm Arducam packages were installed for the correct codename (`bookworm` vs `trixie`).
4. List cameras:
   ```bash
   rpicam-hello --list-cameras
   ```
   or:
   ```bash
   libcamera-hello --list-cameras
   ```
5. Check Arducam’s current IMX519 docs for your exact SKU (overlay name can differ).

### Permission denied writing images

```bash
whoami
```

```bash
ls -ld /home/huxpi/captured_images
```

- If the folder is owned by another user, either use your own `output_dir` in `lemna.py` or fix ownership (only if you intend to use the `huxpi` path):
  ```bash
  sudo mkdir -p /home/huxpi/captured_images
  sudo chown "$(whoami):$(whoami)" /home/huxpi/captured_images
  ```
  Prefer editing `output_dir` to `$HOME/captured_images` if you are not the `huxpi` user.

### Permission / device errors opening the camera

```bash
groups
```

You typically want the `video` group. If it is missing:

```bash
sudo usermod -aG video "$USER"
```

Then **log out and log back in** (or reboot) and try again.

### `python3: No module named 'picamera2'` or `cv2`

```bash
sudo apt install -y python3-picamera2 python3-opencv
```

Avoid `pip install opencv-python` on Raspberry Pi OS unless you know you need it — it can conflict with the apt camera stack.

### Script runs but saves nowhere you expect

Open the script and look at:

```python
output_dir = "/home/huxpi/captured_images"
```

That path is fixed until you change it.

---

## Quick command cheat sheet (after first-time setup)

```bash
sudo apt update
sudo apt install -y python3-picamera2 python3-opencv
mkdir -p /home/huxpi/captured_images
python3 ~/lemna.py
# press c to capture, q to quit
ls /home/huxpi/captured_images/
```
