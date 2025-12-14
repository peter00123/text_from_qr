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
    
    def open_portfolio_link(self):
        """Opens the portfolio URL in a web browser."""
        # Corrected URL opening logic
        url = "https://github.com/peter00123/portfolio"
        try:
            webbrowser.open_new_tab(url)
            messagebox.showinfo("Portfolio", f"Opening link in your browser:\n{url}")
        except Exception as e:
            print(f"Error opening browser: {e}")
            messagebox.showerror("Error", "Could not open web browser.")


    def load_image(self, file_path):
        """Loads and returns the PIL Image object and calculated preview dimensions."""
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        self.image_path = file_path
        self.current_image = Image.open(file_path).convert("L") # Convert to Grayscale on load
        
        max_size = (400, 300)
        preview_img = self.current_image.copy()
        preview_img.thumbnail(max_size)

        return preview_img, self.image_path

    def process_and_resize(self, resize_dim):
        """Resizes the current image to a fixed dimension."""
        if not self.current_image:
            raise ValueError("No image loaded for processing.")
            
        # 1. Resize the actual image (This small image will be used for matrix generation)
        # Using NEAREST resampling for pixel-perfect sampling on small images
        resized_image = self.current_image.resize((resize_dim, resize_dim), Image.Resampling.NEAREST)
        
        return resized_image

    # --- NEW HELPER FUNCTION TO GET PIXEL BRIGHTNESS (Necessary for conversion) ---
    def _get_pixel_brightness(self, image, x, y):
        """
        Gets the pixel brightness (0-255) from a grayscale image.
        Assumes the input image is already converted to 'L' (Grayscale).
        """
        return image.getpixel((x, y))

    # --- UPDATED CHARACTER MATRIX GENERATION METHOD ---
    def generate_character_matrix(self, resized_image):
        """
        Generates the character matrix based on the user's specific mapping:
        Bright (Original '1') -> '0 ' 
        Dark (Original '0') -> '  ' (two spaces)
        """
        # Character map: Index 0 for Dark (0-127), Index 1 for Bright (128-255)
        # We ensure every character representation is exactly two spaces wide.
        NEW_CHAR_MAP = ['0 ','  '] # Dark maps to '  '; Bright maps to '0 '

        matrix = []
        full_text_output = ""
        
        width, height = resized_image.size 

        for y in range(height):
            row = ""
            for x in range(width):
                
                # Check pixel brightness
                brightness = self._get_pixel_brightness(resized_image, x, y)
                
                # Decide if the pixel is Dark (0) or Bright (1)
                char_index = 0 if brightness < 128 else 1 
                
                character = NEW_CHAR_MAP[char_index]
                
                # Store the logical index (0 or 1) in the matrix for image generation later
                # We store '0' or ' ' (space) as single characters in the matrix for image drawing
                # This is a temporary list to correctly map to the image drawing logic.
                matrix_char = ' ' if char_index == 0 else '0' 
                row += matrix_char
                
                # Build the final text output string (using the two-space width)
                full_text_output += character
                
            matrix.append(list(row)) # Convert string row to list for 2D matrix structure
            full_text_output += "\n"
            
        return matrix, full_text_output

    def create_matrix_image(self, matrix):
        """
        Creates a visual image from the character matrix. 
        Note: The matrix now contains single characters ('0' or ' ') for drawing.
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
            font = ImageFont.truetype("arial.ttf", FONT_SIZE)
        except:
            font = ImageFont.load_default()

        # Draw each character
        for y in range(rows):
            for x in range(cols):
                char = str(matrix[y][x])
                
                # Calculate position to center the text in the cell
                # Draw the character only if it's '0' (The ' ' character remains transparent/white background)
                if char == '0':
                    x_pos = x * CELL_SIZE + (CELL_SIZE - FONT_SIZE) // 2
                    y_pos = y * CELL_SIZE + (CELL_SIZE - FONT_SIZE) // 2
                    
                    fill_color = "black"
                    draw.text((x_pos, y_pos), char, fill=fill_color, font=font)
        
        return image

    def save_image(self, image_to_save):
        """Asks user for save location and saves the processed image."""
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
        
    def calculate_display_params(self, matrix_image):
        """Calculates the display parameters based on the newly created matrix image."""
        
        display_w = matrix_image.width
        display_h = matrix_image.height
        
        # 3. Calculate text box character dimensions (approximate)
        text_width_chars = max(1, display_w // CHAR_WIDTH_PX)
        text_height_lines = max(1, display_h // CHAR_HEIGHT_PX)

        return display_w, display_h, text_width_chars, text_height_lines