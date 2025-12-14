# image_logic.py
import os
from PIL import Image, ImageDraw, ImageFont # New Imports
import webbrowser
from tkinter import messagebox, filedialog

# --- Constants (Used for UI sizing/scaling, shared by logic) ---
PREVIEW_WIDTH_PX = 300 
CHAR_WIDTH_PX = 7 
CHAR_HEIGHT_PX = 15 

# --- New Constants for Matrix Image Visualization ---
CELL_SIZE = 20 # Pixel size of each cell in the visualized matrix
FONT_SIZE = 16 # Font size for characters in the visualized matrix

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
        
        max_size = (400, 300)
        preview_img = self.current_image.copy()
        preview_img.thumbnail(max_size)

        return preview_img, self.image_path

    def process_and_resize(self, resize_dim):
        """Resizes the current image to a fixed dimension."""
        if not self.current_image:
            raise ValueError("No image loaded for processing.")
            
        # 1. Resize the actual image (This small image will be used for matrix generation)
        resized_image = self.current_image.resize((resize_dim, resize_dim), Image.Resampling.NEAREST)
        
        return resized_image

    def calculate_display_params(self, matrix_image):
        """Calculates the display parameters based on the newly created matrix image."""
        # The display parameters are now based on the matrix image size
        
        display_w = matrix_image.width
        display_h = matrix_image.height
        
        # 3. Calculate text box character dimensions (approximate)
        text_width_chars = max(1, display_w // CHAR_WIDTH_PX)
        text_height_lines = max(1, display_h // CHAR_HEIGHT_PX)

        return display_w, display_h, text_width_chars, text_height_lines

    def generate_character_matrix(self, resized_image):
        """
        Converts the resized image into a character matrix based on pixel brightness.
        Returns the matrix (2D list of chars) and the matrix as a single string.
        """
        image_mono = resized_image.convert('L')  # Convert to grayscale
        width, height = image_mono.size
        
        # Simple ASCII representation (darker pixels = denser characters)
        # Using 0/1 for binary QR code-like representation
        # You can expand this if you want a true ASCII art effect
        CHAR_MAP = ('1', '0') # 0 for dark (low value), 1 for bright (high value)

        matrix = []
        matrix_string = []
        
        # Note: We iterate over the small, resized image
        for y in range(height):
            row = []
            row_string = []
            for x in range(width):
                brightness = image_mono.getpixel((x, y))
                
                # Assign 0 for dark pixels (value < 128) and 1 for bright pixels
                char = CHAR_MAP[0] if brightness < 128 else CHAR_MAP[1]
                
                row.append(char)
                row_string.append(char)
            matrix.append(row)
            matrix_string.append(" ".join(row_string)) # Add spaces for readability
            
        full_text_output = "\n".join(matrix_string)

        return matrix, full_text_output

    def create_matrix_image(self, matrix):
        """
        Creates a visual image from the character matrix. (User's request)
        """
        rows = len(matrix)
        cols = len(matrix[0])

        # Create image canvas
        img_width = cols * CELL_SIZE
        img_height = rows * CELL_SIZE
        image = Image.new("RGB", (img_width, img_height), "white")
        draw = ImageDraw.Draw(image)

        # Load a font
        try:
            # Attempt to load a common font
            font = ImageFont.truetype("arial.ttf", FONT_SIZE)
        except:
            # Fallback to default font
            font = ImageFont.load_default()

        # Draw each character
        for y in range(rows):
            for x in range(cols):
                char = str(matrix[y][x])
                
                # Calculate position to center the text in the cell
                x_pos = x * CELL_SIZE + (CELL_SIZE - FONT_SIZE) // 2
                y_pos = y * CELL_SIZE + (CELL_SIZE - FONT_SIZE) // 2
                
                # Set color based on content (e.g., black for '0', gray for '1')
                fill_color = "black" if char == '0' else "gray"
                
                draw.text((x_pos, y_pos), char, fill=fill_color, font=font)
        
        return image

    def save_image(self, image_to_save):
        """Asks user for save location and saves the processed image."""
        # Now saves the visually created matrix image
        default_filename = f"matrix_preview_{image_to_save.width}x{image_to_save.height}.png"
        
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