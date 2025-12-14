# image_logic.py
import os
from PIL import Image
import webbrowser
from tkinter import messagebox, filedialog

# --- Constants (Used for UI sizing/scaling, shared by logic) ---
PREVIEW_WIDTH_PX = 300 
CHAR_WIDTH_PX = 7 
CHAR_HEIGHT_PX = 15 

class ImageProcessorLogic:
    """
    Handles all non-Tkinter business logic: file operations, 
    image manipulation, and data calculations.
    """
    def __init__(self):
        self.current_image = None
        self.image_path = None

    def load_image(self, file_path):
        """Loads and returns the PIL Image object and calculated preview dimensions."""
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        self.image_path = file_path
        self.current_image = Image.open(file_path)
        
        # Calculate thumbnail for the *initial* display (max 400x300 for main screen)
        max_size = (400, 300)
        preview_img = self.current_image.copy()
        preview_img.thumbnail(max_size)

        return preview_img, self.image_path

    def process_and_resize(self, resize_dim):
        """Resizes the current image based on the slider value."""
        if not self.current_image:
            raise ValueError("No image loaded for processing.")
            
        # 1. Resize the actual image
        resized_image = self.current_image.resize((resize_dim, resize_dim), Image.Resampling.NEAREST)
        
        # 2. Calculate scaled-up preview dimensions for the ResultScreen
        scale_factor = max(1, PREVIEW_WIDTH_PX // resized_image.width)
        display_w = resized_image.width * scale_factor
        display_h = resized_image.height * scale_factor

        # 3. Calculate text box character dimensions
        text_width_chars = max(1, display_w // CHAR_WIDTH_PX)
        text_height_lines = max(1, display_h // CHAR_HEIGHT_PX)

        return resized_image, display_w, display_h, text_width_chars, text_height_lines

    def save_image(self, image_to_save):
        """Asks user for save location and saves the processed image."""
        default_filename = f"resized_{image_to_save.width}x{image_to_save.height}.png"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_filename,
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )

        if file_path:
            image_to_save.save(file_path)
            messagebox.showinfo("Success", f"Image successfully saved to:\n{file_path}")
            return True
        return False
        
    def open_portfolio_link(self):
        """Opens the portfolio URL in a web browser."""
        url = "hub.com/peter00123/portfolio"
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        webbrowser.open_new_tab(url)
        messagebox.showinfo("Portfolio", f"Opening link in your browser:\n{url}")