# Python Image Cropper

A simple and advanced **Python Tkinter application** to crop images with live rectangle selection, resizing, and color control.

## Features

- Open images in multiple formats (`PNG`, `JPEG`, `BMP`, `WEBP`).
- Crop images by drawing a rectangle with the mouse.
- Resize crop rectangle from corners.
- Move the crop rectangle by dragging inside it.
- Automatic cleanup of previous crop rectangle when creating a new one.
- Dynamic cursor indicating actions (`cross`, `fleur`, `sizing`).
- Crop rectangle color can be adjusted using a slider.
- Save cropped images in `PNG` or `JPEG` format.
- Window automatically opens with image size or fullscreen for large images.
- Works with Dolphin file manager via context menu (file path can be passed as argument).

## Requirements

- Python 3.x
- Pillow (`pip install pillow`)
- Tkinter (usually included with Python)

## Installation

1. Clone the repository or download the source files:

```bash
git clone https://github.com/reiokr/python-image-cropper.git
cd python-image-cropper
```

2. Make the script executable:

```bash
chmod +x python-image-cropper.py
```

3. Run the application:

```bash
./python-image-cropper.py
```

Or pass an image file directly:

```bash
./python-image-cropper.py path/to/image.png
```

## Usage

1. **Open an image** using the "Open Image" button or pass the file as an argument.
2. **Draw a crop rectangle** by clicking and dragging on the image.
3. **Resize** the rectangle using the red corner handles.
4. **Move** the rectangle by dragging inside it.
5. **Adjust rectangle color** using the color slider.
6. **Save cropped image** using the "Save Crop" button.
7. **Clear rectangle** using the "Clear" button if needed.
8. **Exit** the app using the "Exit" button.

## Using Dolphin Context Menu (Linux)

You can integrate the cropper into Dolphin to open images directly from the file manager:

1. Open Dolphin and navigate to:\
   `Settings → Configure Dolphin → Services → Download New Services → Download Menu`.

2. Alternatively, create a `.desktop` file in `~/.local/share/kio/servicemenus/`:

```ini
[Desktop Entry]
Type=Service
ServiceTypes=KonqPopupMenu/Plugin
MimeType=image/png;image/jpeg;image/bmp;
Actions=OpenWithCropper;
X-KDE-Priority=TopLevel

[Desktop Action OpenWithCropper]
Name=Open with Image Cropper
Exec=/path/to/python-image-cropper.py %f
Icon=applications-graphics
```

- Replace `/path/to/python-image-cropper.py` with the actual path to your script.
- After saving, restart Dolphin.
- Right-click any image → "Open with Image Cropper" → the app opens with the selected image.

## Screenshots


## License

MIT License – see [LICENSE](LICENSE) file for details.

