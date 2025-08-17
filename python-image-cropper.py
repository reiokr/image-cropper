import sys
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os

HANDLE_SIZE = 8
DEFAULT_IMAGE_DIR = os.path.join(os.path.expanduser("~"), "Pildid")

class ImageCropper:
    def __init__(self, root, initial_file=None):
        self.root = root
        self.root.title("Image Cropping App")

        # Frame Canvas'ile
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, cursor="cross", bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Alumine nuppude riba
        self.button_frame = tk.Frame(root, height=50)
        self.button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.button_frame.pack_propagate(False)

        # Väldi, et akent saaks liiga väikeseks teha (nupud alati nähtavad)
        self.root.update_idletasks()
        btn_h = self.button_frame.winfo_height() or 50
        min_w = 400   # vähemalt nii lai
        min_h = btn_h + 200  # vähemalt nii kõrge (pildi jaoks ruum ka)
        self.root.minsize(min_w, min_h)

        self.btn_open = tk.Button(self.button_frame, text="Open Image", command=self.open_image)
        self.btn_save = tk.Button(self.button_frame, text="Save Crop", command=self.save_crop)
        self.btn_clear = tk.Button(self.button_frame, text="Clear", command=self.clear_crop)
        self.btn_exit = tk.Button(self.button_frame, text="Exit", command=root.quit)

        for btn in [self.btn_open, self.btn_save, self.btn_clear]:
            btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_exit.pack(side=tk.RIGHT, padx=5, pady=5)

        # Muutujad
        self.image = None
        self.display_image = None
        self.tk_image = None
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.crop_coords = None
        self.dragging = False
        self.resizing = None
        self.dragging_rect = False
        self.offset_x = 0
        self.offset_y = 0

        # Eventid
        self.root.bind("<Configure>", self.on_resize)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Motion>", self.on_mouse_move)

        if initial_file:
            self.load_image(initial_file)


    def open_image(self, path=None):
        if not path:
            path = filedialog.askopenfilename(
                initialdir=DEFAULT_IMAGE_DIR,
                filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.webp *.gif")],)
            if not path:
                return
        self.load_image(path)


    def load_image(self, path):
        try:
            self.image = Image.open(path)
        except Exception as e:
            print(f"Error loading image: {e}")
            return

        # Get screen size
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        img_w, img_h = self.image.size

        # Reserve space for button frame
        self.root.update_idletasks()
        btn_h = self.button_frame.winfo_height() or 50  # fallback kui veel null

        # Check scaling
        if img_w > screen_w or img_h + btn_h > screen_h:
            scale = min((screen_w / img_w), (screen_h - btn_h) / img_h)
            new_w, new_h = int(img_w * scale), int(img_h * scale)
            self.display_image = self.image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        else:
            self.display_image = self.image.copy()

        # Update window size
        disp_w, disp_h = self.display_image.size
        self.root.geometry(f"{disp_w}x{disp_h + btn_h}")

        self.show_image()
        self.clear_crop()
        self.root.update_idletasks()

    def scale_image_to_canvas(self):
        btn_h = self.button_frame.winfo_height() or 50
        if not self.image:
            return
        canvas_width = self.root.winfo_width()
        canvas_height = self.root.winfo_height() - btn_h
        if canvas_width < 100 or canvas_height < 100:
            canvas_width, canvas_height = 800, 600
        image_width, image_height = self.image.size
        try:
            scale_factor = min(canvas_width / image_width, canvas_height / image_height, 1)
            resized_width = int(image_width * scale_factor)
            resized_height = int(image_height * scale_factor)
            self.display_image = self.image.resize((resized_width, resized_height), Image.Resampling.LANCZOS)

            self.root.geometry(f"{resized_width}x{resized_height + btn_h}")

        except (ValueError, ZeroDivisionError):
            print("Error resizing image")
        

    def show_image(self):
        if not self.display_image:
            return
        self.tk_image = ImageTk.PhotoImage(self.display_image)
        self.canvas.delete("all")
        self.canvas.config(width=self.display_image.size[0], height=self.display_image.size[1])
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        if self.crop_coords:
            self.draw_rect()

    # --- Crop rectangle ---
    def draw_rect(self):
        self.canvas.delete("crop")
        if not self.crop_coords:
            return
        x0, y0, x1, y1 = self.crop_coords
        self.rect = self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", width=2, tags="crop")
        for cx, cy in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:
            self.canvas.create_rectangle(cx-HANDLE_SIZE//2, cy-HANDLE_SIZE//2,
                                         cx+HANDLE_SIZE//2, cy+HANDLE_SIZE//2,
                                         fill="red", tags="crop")

    def clear_crop(self):
        self.crop_coords = None
        self.rect = None
        self.show_image()
        

    # --- Mouse eventid ---
    def on_mouse_down(self, event):
        if not self.display_image:
            return
        handle = self.get_handle(event.x, event.y)
        if handle:
            self.resizing = handle
            self.dragging = False
            self.dragging_rect = False
        elif self.is_inside_rect(event.x, event.y):
            self.dragging_rect = True
            self.dragging = False
            self.resizing = None
            x0, y0, x1, y1 = self.crop_coords
            self.offset_x = event.x - min(x0, x1)
            self.offset_y = event.y - min(y0, y1)
        else:
            self.clear_crop()
            self.start_x, self.start_y = event.x, event.y
            self.crop_coords = (self.start_x, self.start_y, self.start_x, self.start_y)
            self.dragging = True
            self.dragging_rect = False
            self.resizing = None
        self.draw_rect()

    def on_mouse_drag(self, event):
        if not self.display_image or not self.crop_coords:
            return
        x, y = event.x, event.y
        if self.resizing:
            x0, y0, x1, y1 = self.crop_coords
            if "n" in self.resizing: y0 = y
            if "s" in self.resizing: y1 = y
            if "w" in self.resizing: x0 = x
            if "e" in self.resizing: x1 = x
            self.crop_coords = (x0, y0, x1, y1)
        elif self.dragging_rect:
            x0, y0, x1, y1 = self.crop_coords
            w = x1 - x0
            h = y1 - y0
            new_x0 = x - self.offset_x
            new_y0 = y - self.offset_y
            self.crop_coords = (new_x0, new_y0, new_x0 + w, new_y0 + h)
        elif self.dragging:
            self.crop_coords = (self.start_x, self.start_y, x, y)
        self.draw_rect()

    def on_mouse_up(self, event):
        self.dragging = False
        self.resizing = None
        self.dragging_rect = False

    def get_handle(self, x, y):
        if not self.crop_coords:
            return None
        x0, y0, x1, y1 = self.crop_coords
        handles = {"nw": (x0, y0), "ne": (x1, y0), "sw": (x0, y1), "se": (x1, y1)}
        for name, (hx, hy) in handles.items():
            if abs(x - hx) <= HANDLE_SIZE and abs(y - hy) <= HANDLE_SIZE:
                return name
        return None

    def is_inside_rect(self, x, y):
        if not self.crop_coords:
            return False
        x0, y0, x1, y1 = self.crop_coords
        return min(x0, x1) <= x <= max(x0, x1) and min(y0, y1) <= y <= max(y0, y1)

    def on_mouse_move(self, event):
        if not self.crop_coords:
            self.canvas.config(cursor="cross")
            return
        handle = self.get_handle(event.x, event.y)
        if handle:
            self.canvas.config(cursor="sizing")
        elif self.is_inside_rect(event.x, event.y):
            self.canvas.config(cursor="fleur")
        else:
            self.canvas.config(cursor="cross")

    def on_resize(self, event):

        if not self.image:
            return
        win_w, win_h = self.root.winfo_width(), self.root.winfo_height()
        img_w, img_h = self.display_image.size
        if abs(win_w - img_w) > 50 or abs(win_h - img_h) > 50:
            self.scale_image_to_canvas()
            self.show_image()

    # --- Salvestamine ---
    def save_crop(self):
        if self.image and self.crop_coords:
            orig_w, orig_h = self.image.size
            disp_w, disp_h = self.display_image.size
            scale_x = orig_w / disp_w
            scale_y = orig_h / disp_h
            x0, y0, x1, y1 = self.crop_coords
            crop_coords_orig = (int(min(x0, x1) * scale_x), int(min(y0, y1) * scale_y),
                                int(max(x0, x1) * scale_x), int(max(y0, y1) * scale_y))
            cropped = self.image.crop(crop_coords_orig)
            save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
            if save_path:
                cropped.save(save_path)
                print(f"Image saved: {save_path}")



if __name__ == "__main__":
    initial_file = sys.argv[1] if len(sys.argv) > 1 else None
    root = tk.Tk()
    root.geometry("900x700")
    app = ImageCropper(root, initial_file)
    root.mainloop()
