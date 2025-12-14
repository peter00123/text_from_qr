# image_logic.py
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
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
        # Using a complete, protocol-prefixed URL
        url = "https://github.com/peter00123/portfolio" 
        try:
            webbrowser.open_new_tab(url)
            messagebox.showinfo("Portfolio", f"Opening link in your browser:\n{url}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open web browser: {e}")

    def load_image(self, file_path):
        """Loads and returns the PIL Image object and calculated preview dimensions."""
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        self.image_path = file_path
        # Convert to Grayscale ('L') immediately for consistent brightness calculation
        self.current_image = Image.open(file_path).convert("L") 
        
        max_size = (400, 300)
        preview_img = self.current_image.copy()
        preview_img.thumbnail(max_size)

        return preview_img, self.image_path

    def process_and_resize(self, resize_dim):
        """
        Resizes the current image to a fixed, even dimension to allow for 2x2 compression.
        """
        if not self.current_image:
            raise ValueError("No image loaded for processing.")
            
        # Ensure the dimension is even for 2x2 compression
        final_dim = resize_dim if resize_dim % 2 == 0 else resize_dim - 1
        if final_dim < 10:
             final_dim = 10 
        
        # Resize to the final even dimension
        resized_image = self.current_image.resize((final_dim, final_dim), Image.Resampling.NEAREST)
        
        return resized_image

    def _get_pixel_brightness(self, image, x, y):
        """Gets the pixel brightness (0-255) from a grayscale image."""
        return image.getpixel((x, y))

    def _compress_and_format_matrix(self, single_char_matrix):
        """
        Compresses the matrix by a 2x2 factor using a 'Majority Wins' rule.
        SWAPS: Bright areas are '  ', Dark areas are '# '.
        """
        rows = len(single_char_matrix)
        cols = len(single_char_matrix[0])
        
        compressed_matrix = []
        full_text_output = ""
        
        for y in range(0, rows, 2):
            new_row = []
            text_row = ""
            for x in range(0, cols, 2):
                
                # Extract the 2x2 block
                block = [
                    single_char_matrix[y][x], single_char_matrix[y][x+1],
                    single_char_matrix[y+1][x], single_char_matrix[y+1][x+1]
                ]
                
                # Count the bright pixels ('#'). 
                hash_count = block.count('#')
                
                # --- Majority Wins Rule (2 or more '#' means the block is considered bright) ---
                if hash_count >= 2:
                    # Original logic: Bright. Now: Represented by Dark Text.
                    char = ' '                     # Character for Image (Space)
                    text_char_output = '  '        # Text Output (Two spaces)
                else:
                    # Original logic: Dark. Now: Represented by Bright Text.
                    char = '#'                     # Character for Image (Hash)
                    text_char_output = '# '        # Text Output (Hash + space)

                new_row.append(char)
                text_row += text_char_output
                
            compressed_matrix.append(new_row)
            full_text_output += text_row + "\n"
            
        return compressed_matrix, full_text_output

    def generate_character_matrix(self, resized_image):
        """
        Generates a preliminary matrix of single characters ('#' or ' ') and then 
        passes it to the compression logic.
        """
        matrix_single_char = []
        width, height = resized_image.size 
        
        for y in range(height):
            row = []
            for x in range(width):
                brightness = self._get_pixel_brightness(resized_image, x, y)
                # Bright pixels (>= 128) map to '#', Dark pixels (< 128) map to ' '
                char = '#' if brightness >= 128 else ' ' 
                row.append(char)
            matrix_single_char.append(row)
            
        # Pass the full-resolution matrix to the compression function
        compressed_matrix, full_text_output = self._compress_and_format_matrix(matrix_single_char)
        
        # Return the compressed matrix for image drawing, and the final text output
        return compressed_matrix, full_text_output

    def create_matrix_image(self, matrix):
        """
        Creates a visual image from the compressed character matrix (only '#' or ' '). 
        Note: The image drawing uses the 'char' assigned in the compression step. 
              Since we swapped the 'char' values, the image visualization is now also inverted.
        """
        if not matrix or not matrix[0]: return Image.new("RGB", (10, 10), "white")
        
        rows = len(matrix)
        cols = len(matrix[0])

        # Create image canvas
        img_width = cols * CELL_SIZE
        img_height = rows * CELL_SIZE
        image = Image.new("RGB", (img_width, img_height), "white")
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", FONT_SIZE)
        except:
            font = ImageFont.load_default()

        # Draw each character from the compressed matrix
        for y in range(rows):
            for x in range(cols):
                char = str(matrix[y][x])
                
                # We only draw '#' characters (which now represent the dark areas of the source image)
                if char == '#':
                    # Center the text in the cell
                    x_pos = x * CELL_SIZE + (CELL_SIZE - FONT_SIZE) // 2
                    y_pos = y * CELL_SIZE + (CELL_SIZE - FONT_SIZE) // 2
                    
                    fill_color = "black"
                    draw.text((x_pos, y_pos), char, fill=fill_color, font=font)
                # If char == ' ' (which now represents the bright areas), we skip drawing.
                
        return image

    def save_image(self, image_to_save):
        """Asks user for save location and saves the processed image."""
        # Calculate compressed size for default filename
        rows = image_to_save.height // CELL_SIZE
        cols = image_to_save.width // CELL_SIZE
        default_filename = f"compressed_matrix_inverted_{cols}x{rows}.png"
        
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
        
        # Calculate text box character dimensions (approximate)
        text_width_chars = max(1, display_w // CHAR_WIDTH_PX)
        text_height_lines = max(1, display_h // CHAR_HEIGHT_PX)

        return display_w, display_h, text_width_chars, text_height_lines