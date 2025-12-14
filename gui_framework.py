import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
from tkinterdnd2 import DND_ALL, TkinterDnD 
from image_logic import ImageProcessorLogic, CELL_SIZE 
import os

# --- Layout Constants for Fixed Sizing ---
PANE_WIDTH = 380 
PANE_HEIGHT = 550
PANE_BG = "#f5f5f5"

# --- Tooltip Class ---
class Tooltip:
    """Creates a temporary, non-blocking pop-up message near a widget."""
    def __init__(self, widget, text, delay_ms=3000):
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self.tip_window = None
        self.timeout_id = None
        self.show()

    def show(self):
        if self.tip_window or not self.widget.winfo_exists():
            return
            
        x = self.widget.winfo_rootx() + self.widget.winfo_width()
        y = self.widget.winfo_rooty()

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))

        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)
        
        self.timeout_id = self.widget.after(self.delay_ms, self.hide)

    def hide(self):
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None
        if self.timeout_id:
            self.widget.after_cancel(self.timeout_id)
            self.timeout_id = None
# ----------------------------------------------------------------------


class ImageProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Matrix Generator (Fixed 3-Pane Layout)")
        # Calculate window size based on 3 panes + padding
        total_width = (PANE_WIDTH * 3) + 60
        total_height = PANE_HEIGHT + 100
        self.root.geometry(f"{total_width}x{total_height}") 
        self.root.resizable(False, False) # Lock the size

        self.logic = ImageProcessorLogic() 
        self.photo = None 
        self.resized_photo = None 
        self.current_matrix_image = None # PIL Image of the final character matrix (used for Download)
        
        # --- Top Bar ---
        self.top_bar = tk.Frame(root, height=30)
        self.top_bar.pack(fill=tk.X, padx=10, pady=(5, 0))
        self.setup_top_bar(self.top_bar)
        
        # --- Main 3-Pane Container ---
        self.main_container = tk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- Setup the Three Panes ---
        self.setup_input_pane(self.main_container)
        self.setup_preview_pane(self.main_container)
        self.setup_output_pane(self.main_container)
        
        # Initial status text
        self.text_output.insert(tk.END, "Load an image and click Refresh to generate the character matrix.")

        # Bind the slider change only to update the label, NOT the matrix
        self.slider.config(command=self.update_slider_value) 
        
    def setup_top_bar(self, frame):
        tk.Label(frame).pack(side=tk.LEFT, expand=True) 

        self.how_to_use_button = tk.Button(
            frame, 
            text="ⓘ How to Use", 
            command=self.logic.open_portfolio_link,
            relief=tk.FLAT, 
            fg="blue"
        )
        self.how_to_use_button.pack(side=tk.RIGHT)
        
        self.root.after(100, lambda: self.show_tooltip_popup(self.how_to_use_button))

    def show_tooltip_popup(self, widget):
        message = "Click here for instructions or visit the portfolio link!"
        Tooltip(widget, message, delay_ms=4000)


    # --- PANE 1: INPUT/CONTROL (Fixed Size) ---
    def setup_input_pane(self, container):
        self.input_pane = tk.Frame(
            container, 
            width=PANE_WIDTH, 
            height=PANE_HEIGHT, 
            padx=10, 
            pady=10, 
            relief=tk.GROOVE, 
            borderwidth=2, 
            bg=PANE_BG
        )
        self.input_pane.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.input_pane.pack_propagate(False)

        tk.Label(self.input_pane, text="1. Image Input & Size", font=("Arial", 14, "bold"), bg=PANE_BG).pack(pady=5)

        # Frame for Image Label to control its size within the fixed pane
        img_frame = tk.Frame(self.input_pane, bg="lightgray", height=200)
        img_frame.pack(pady=10, padx=10, fill=tk.X)
        img_frame.pack_propagate(False) # Fix the size of the image frame

        self.image_label = tk.Label(
            img_frame, text="Drag & Drop Image Here\nor Click to Browse",
            bg="lightgray"
        )
        self.image_label.pack(fill=tk.BOTH, expand=True)
        self.image_label.bind("<Button-1>", self.browse_image)
        self.image_label.drop_target_register(DND_ALL) 
        self.image_label.dnd_bind('<<Drop>>', self.drop_image) 
        
        tk.Button(self.input_pane, text="Browse Image", command=self.browse_image).pack(pady=(0, 10))
        
        tk.Label(self.input_pane, text="Matrix Dimension (10 to 200 pixels):", bg=PANE_BG).pack()
        self.slider = tk.Scale(
            self.input_pane, from_=10, to=200, orient=tk.HORIZONTAL, length=300, 
            resolution=1
        )
        self.slider.set(50)
        self.slider.pack(pady=5, padx=10, fill=tk.X)
        self.slider_value = tk.Label(self.input_pane, text="Value: 50", bg=PANE_BG)
        self.slider_value.pack()
        
        # Submit/Refresh Button
        tk.Button(self.input_pane, text="Refresh Matrix", command=self.refresh_matrix, bg="#0088AA", fg="white", padx=20, pady=5).pack(pady=20)
        tk.Button(self.input_pane, text="Download Matrix Image", command=self.download_image, bg="blue", fg="white", padx=10, pady=5).pack()


    # --- PANE 2: PREVIEW (Single Box, Fixed Size) ---
    def setup_preview_pane(self, container):
        self.preview_pane = tk.Frame(
            container, 
            width=PANE_WIDTH, 
            height=PANE_HEIGHT, 
            padx=10, 
            pady=10, 
            relief=tk.GROOVE, 
            borderwidth=2, 
            bg=PANE_BG
        )
        self.preview_pane.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        self.preview_pane.pack_propagate(False)

        # --- SINGLE BOX: Resized Source Image ---
        tk.Label(self.preview_pane, text="2. Resized Source Image (Source for Matrix)", font=("Arial", 14, "bold"), bg=PANE_BG).pack(pady=5)
        
        # This label will expand to fill the available space
        self.resized_preview_label = tk.Label(
            self.preview_pane,
            text="Original Image scaled to matrix size (e.g., 50x50)",
            bg="white",
            relief=tk.RIDGE
        )
        self.resized_preview_label.pack(pady=5, fill=tk.BOTH, expand=True)

        self.size_info_label = tk.Label(self.preview_pane, text="Output size: N/A", bg=PANE_BG)
        self.size_info_label.pack(pady=5)


    # --- PANE 3: TEXT OUTPUT (Fixed Size & Scrollable) ---
    def setup_output_pane(self, container):
        self.output_pane = tk.Frame(
            container, 
            width=PANE_WIDTH, 
            height=PANE_HEIGHT, 
            padx=10, 
            pady=10, 
            relief=tk.GROOVE, 
            borderwidth=2, 
            bg=PANE_BG
        )
        self.output_pane.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))
        self.output_pane.pack_propagate(False)

        tk.Label(self.output_pane, text="3. Character Matrix Output", font=("Arial", 14, "bold"), bg=PANE_BG).pack(pady=5)

        # Control Frame for Copy Button
        text_control_frame = tk.Frame(self.output_pane, bg=PANE_BG)
        text_control_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(text_control_frame, text="Matrix Text (Scrollable):", bg=PANE_BG).pack(side=tk.LEFT)
        tk.Button(
            text_control_frame, 
            text="Copy Text", 
            command=self.copy_text,
            bg="#e0e0e0"
        ).pack(side=tk.RIGHT)
        
        # Text Widget for Output with Scrollbars (ScrolledText is simpler)
        self.text_output = scrolledtext.ScrolledText(
            self.output_pane, 
            wrap=tk.NONE, # Important for ASCII/matrix output
            font=("Courier", 8),
            bg="#f0f0f0",
            relief=tk.SUNKEN
        )
        self.text_output.pack(pady=5, fill=tk.BOTH, expand=True)

    
    # --- HANDLERS ---
    def browse_image(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")])
        if file_path:
            self._display_loaded_image(file_path)
    
    def drop_image(self, event):
        file_path = event.data.strip().strip('{}')
        if ' ' in file_path: file_path = file_path.split(' ')[0]
             
        if os.path.isfile(file_path):
            self._display_loaded_image(file_path)
        else:
            messagebox.showerror("Error", f"Invalid file path dropped: {file_path}")
    
    def _display_loaded_image(self, file_path):
        """Calls logic to load image and updates the UI in the input pane."""
        try:
            # Load the original image for the small thumbnail preview
            preview_img, _ = self.logic.load_image(file_path)
            
            # Convert PIL image for Tkinter display (small thumbnail for Input Pane)
            self.photo = ImageTk.PhotoImage(preview_img)
            self.image_label.config(image=self.photo, text="")
            self.image_label.image = self.photo
        except Exception as e:
            messagebox.showerror("Error Loading Image", f"Could not load image: {e}")
            self.image_label.config(image=None, text="Error loading image.\nClick to browse.")
            self.logic.current_image = None
            
        # Clear previous outputs when a new image is loaded
        self.text_output.delete("1.0", tk.END)
        self.text_output.insert(tk.END, "New image loaded. Click 'Refresh Matrix' to generate.")
        self.resized_preview_label.config(image=None, text="Original Image scaled to matrix size (e.g., 50x50)")
    
    def update_slider_value(self, value):
        self.slider_value.config(text=f"Value: {value}")

    # The main processing function, only called by the Refresh button
 # The main processing function, only called by the Refresh button
    def refresh_matrix(self):
        """
        Processes the image using the current slider value and updates the preview
        and text output panes, ensuring the resized image fits the pane.
        """
        if not self.logic.current_image:
            self.text_output.delete("1.0", tk.END)
            self.text_output.insert(tk.END, "Error: Please load an image first.")
            return
            
        resize_dim = self.slider.get()
        try:
            # --- Logic Calls ---
            resized_image_pil = self.logic.process_and_resize(resize_dim)
            matrix, full_text_output = self.logic.generate_character_matrix(resized_image_pil)
            matrix_image_pil = self.logic.create_matrix_image(matrix)
            self.current_matrix_image = matrix_image_pil # Store PIL Image for the Download button

            # 4. Calculate display parameters based on the new matrix image size (Logic)
            display_w, display_h, text_w, text_h = self.logic.calculate_display_params(matrix_image_pil)
            
            
            # --- Update Preview Pane 2 (Resized Source Image) ---
            
            # Maximum drawable space in Pane 2 (Pane dimensions - padding/labels)
            # This accounts for the top title and the bottom size_info_label.
            max_width_drawable = PANE_WIDTH - 40   # 380 - (10*2 padding) - (20 margin for safety)
            max_height_drawable = PANE_HEIGHT - 90 # 550 - (approx 90px for labels/margins)
            
            # Create a copy of the *resized* image for the preview
            source_preview = resized_image_pil.copy()
            
            # Scale the image to fit the maximum drawable area while maintaining aspect ratio
            source_preview.thumbnail((max_width_drawable, max_height_drawable))
            
            self.resized_photo = ImageTk.PhotoImage(source_preview)
            
            # Set the image and ensure the label resizes to contain it within the pane
            # We set the label width/height to the actual image size, but the label's packing (expand=True)
            # ensures it is centered within the fixed pane space.
            self.resized_preview_label.config(
                image=self.resized_photo,
                text=f"Source Image ({resize_dim}x{resize_dim}) Preview",
                compound=tk.CENTER,
                width=source_preview.width,
                height=source_preview.height,
                relief=tk.FLAT,
                bg="lightgray" # Set background of the label to see its boundaries
            )
            self.resized_preview_label.image = self.resized_photo
            
            # --- Update Status Info ---
            char_w = len(matrix[0]) if matrix and matrix[0] else 0
            char_h = len(matrix) if matrix else 0
            self.size_info_label.config(text=f"Matrix Size: {char_w}x{char_h} characters (Source: {resize_dim}x{resize_dim} pixels)")
            
            # --- Update Output Pane 3 ---
            self.text_output.delete("1.0", tk.END)
            self.text_output.insert(tk.END, full_text_output)
            
        except Exception as e:
            messagebox.showerror("Processing Error", f"An error occurred during matrix generation: {e}")
            self.text_output.delete("1.0", tk.END)
            self.text_output.insert(tk.END, f"Error: {e}")
            
    def copy_text(self):
        """Copies the content of the text widget using Tkinter's clipboard functions."""
        try:
            # Get text directly from the ScrolledText widget
            text_to_copy = self.text_output.get("1.0", tk.END).strip()
            
            self.root.clipboard_clear()
            self.root.clipboard_append(text_to_copy)
            messagebox.showinfo("Copied", "Matrix content copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Copy Error", f"Could not copy text: {e}")

    def download_image(self):
        """Calls logic to save the matrix image."""
        if not self.current_matrix_image:
            messagebox.showerror("Error", "No matrix image generated to save.")
            return

        try:
            self.logic.save_image(self.current_matrix_image)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save image: {e}")

            