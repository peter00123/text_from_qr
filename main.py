import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
# New import for Drag-and-Drop functionality
# Import the main class and constant from the installed package
from tkinterdnd2 import TkinterDnD, DND_ALL




class ImageProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")
        self.root.geometry("500x700")
        
        # --- Variables ---
        self.current_image = None  # Holds the PIL Image object
        self.image_path = None
        self.photo = None
        
        # --- Setup Main Container ---
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_main_screen(self.main_frame)

    def setup_main_screen(self, frame):
        """Sets up the widgets for the image loading and adjustment screen."""
        
        # Clear any previous widgets in the frame
        for widget in frame.winfo_children():
            widget.destroy()

        # Image display area with drag and drop
        self.image_label = tk.Label(
            frame, text="Drag & Drop Image Here\nor Click to Browse",
            bg="lightgray", height=10, width=50
        )
        self.image_label.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.image_label.bind("<Button-1>", self.browse_image)
        
        # DnD Setup
        self.image_label.drop_target_register(DND_ALL) 
        self.image_label.dnd_bind('<<Drop>>', self.drop_image) 
        
        # Browse button
        tk.Button(frame, text="Browse Image", command=self.browse_image).pack(pady=5)
        
        # Slider for Resize Value
        tk.Label(frame, text="Resize Dimension (10 to 200 pixels):").pack()
        self.slider = tk.Scale(
            frame, from_=10, to=200, orient=tk.HORIZONTAL, length=300, 
            resolution=1 # Ensure whole numbers for pixel size
        )
        self.slider.set(50) # Set a sensible default
        self.slider.pack(pady=5, padx=10, fill=tk.X)
        self.slider_value = tk.Label(frame, text="Value: 50")
        self.slider_value.pack()
        self.slider.config(command=self.update_slider_value)
        
        # Submit button
        tk.Button(frame, text="Submit & Resize", command=self.submit, bg="green", fg="white").pack(pady=20)
    
    # --- Image Loading Handlers ---
    
    def browse_image(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")])
        if file_path:
            self.load_image(file_path)
    
    def drop_image(self, event):
        file_path = event.data.strip()
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        if ' ' in file_path:
             file_path = file_path.split(' ')[0]
             
        if os.path.isfile(file_path):
            self.load_image(file_path)
        else:
            messagebox.showerror("Error", f"Invalid file path dropped: {file_path}")
    
    def load_image(self, file_path):
        """Loads and displays the image."""
        self.image_path = file_path
        try:
            self.current_image = Image.open(file_path)
            
            # Preview size (fixed for display)
            max_size = (400, 300)
            
            # Create a thumbnail for the preview label
            preview_img = self.current_image.copy()
            preview_img.thumbnail(max_size)
            
            self.photo = ImageTk.PhotoImage(preview_img)
            self.image_label.config(image=self.photo, text="")
            self.image_label.image = self.photo # Keep reference
            
        except Exception as e:
            messagebox.showerror("Error Loading Image", f"Could not load image: {e}")
            self.image_label.config(image=None, text="Error loading image.\nClick to browse.")
            self.current_image = None
    
    def update_slider_value(self, value):
        self.slider_value.config(text=f"Value: {value}")
    
    def submit(self):
        """Processes the image and switches to the result screen."""
        if not self.current_image:
            messagebox.showerror("Error", "Please select an image before submitting.")
            return
            
        resize_dim = self.slider.get()
        
        # 1. Resize the Image (The Core Logic)
        try:
            # We resize the original image to the square dimension specified by the slider.
            resized_image = self.current_image.resize((resize_dim, resize_dim), Image.Resampling.NEAREST)
        
            # 2. Hide the main frame and show the result screen
            self.main_frame.pack_forget()
            
            # Create and show the result screen
            self.result_screen = ResultScreen(
                self.root, 
                resized_image, 
                self.go_back_to_main
            )
            self.result_screen.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Processing Error", f"Could not resize image: {e}")
            self.main_frame.pack(fill=tk.BOTH, expand=True) # Show main screen if error occurs

    def go_back_to_main(self):
        """Switches back from the result screen to the main screen."""
        self.result_screen.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        # Re-display the loaded image on the main screen after coming back
        if self.image_path:
             self.load_image(self.image_path)


class ResultScreen(tk.Frame):
    """A separate screen to display the resized image and save/redo buttons."""
    def __init__(self, master, image_to_preview, redo_callback):
        super().__init__(master)
        self.resized_image = image_to_preview
        self.redo_callback = redo_callback
        self.photo = None # To hold the ImageTk reference

        self.setup_result_screen()

    def setup_result_screen(self):
        tk.Label(self, text="Image Preview (Resized)", font=("Arial", 16, "bold")).pack(pady=10)

        # 1. Display the preview
        # Scale up the small image for better viewing in the GUI, using NEAREST for sharp pixels
        preview_width = 300 
        scale_factor = preview_width // self.resized_image.width
        display_img = self.resized_image.resize(
            (self.resized_image.width * scale_factor, self.resized_image.height * scale_factor), 
            Image.Resampling.NEAREST
        )

        self.photo = ImageTk.PhotoImage(display_img)
        preview_label = tk.Label(self, image=self.photo, text="")
        preview_label.pack(pady=10)
        preview_label.image = self.photo # Keep reference
        
        tk.Label(self, text=f"Original Size: ({self.resized_image.width}x{self.resized_image.height})").pack(pady=5)

        # 2. Button Frame
        button_frame = tk.Frame(self)
        button_frame.pack(pady=30)

        # Redo Button
        tk.Button(
            button_frame, 
            text="Redo (Go Back)", 
            command=self.redo_callback,
            bg="orange", 
            fg="white",
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=20)

        # Download Button
        tk.Button(
            button_frame, 
            text="Download & Save", 
            command=self.download_image,
            bg="blue", 
            fg="white",
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=20)

    def download_image(self):
        """Asks the user for a save location and saves the resized image."""
        
        # Suggest a default filename based on the new size
        default_filename = f"resized_{self.resized_image.width}x{self.resized_image.height}.png"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_filename,
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            try:
                # Save the actual resized image (not the scaled-up preview)
                self.resized_image.save(file_path)
                messagebox.showinfo("Success", f"Image successfully saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save image: {e}")

if __name__ == "__main__":
    # *** IMPORTANT CHANGE: Use TkinterDnD.Tk() for Drag-and-Drop ***
    root = TkinterDnD.Tk()
    app = ImageProcessorGUI(root)
    root.mainloop()
# Then, when creating the root window, you use:
# root = TkinterDnD.Tk()

# Change the base class of the GUI to inherit from the DnD-enabled Tkinter
class ImageProcessorGUI:
    # Use TkinterDnD.Tk() instead of tk.Tk() later
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")
        self.root.geometry("500x700")
        self.image_path = None
        self.photo = None
        
        # Image display area with drag and drop
        self.image_label = tk.Label(
            root, text="Drag & Drop Image Here\nor Click to Browse",
            bg="lightgray", height=10, width=50
        )
        self.image_label.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.image_label.bind("<Button-1>", self.browse_image)
        
        # --- CORRECTED DnD Bindings ---
        # 1. Register the label as a drop target for files (DND_ALL)
        self.image_label.drop_target_register(DND_ALL) 
        # 2. Bind the correct virtual event for drop
        self.image_label.dnd_bind('<<Drop>>', self.drop_image) 
        # ------------------------------
        
        # Browse button
        tk.Button(root, text="Browse Image", command=self.browse_image).pack(pady=5)
        
        # Slider
        tk.Label(root, text="Adjustment:").pack()
        self.slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, length=300)
        self.slider.pack(pady=5, padx=10, fill=tk.X)
        self.slider_value = tk.Label(root, text="Value: 0")
        self.slider_value.pack()
        self.slider.config(command=self.update_slider_value)
        
        # Input boxes
        tk.Label(root, text="Input 1:").pack()
        self.input1 = tk.Entry(root, width=40)
        self.input1.pack(pady=5, padx=10)
        
        tk.Label(root, text="Input 2:").pack()
        self.input2 = tk.Entry(root, width=40)
        self.input2.pack(pady=5, padx=10)
        
        # Submit button
        tk.Button(root, text="Submit", command=self.submit, bg="green", fg="white").pack(pady=20)
    
    def browse_image(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")])
        if file_path:
            self.load_image(file_path)
    
    def drop_image(self, event):
        # The file path is returned as a string that might be wrapped in braces or quotes
        # We need to clean it up. TkinterDnD2 usually returns a single path directly 
        # or a list of paths separated by spaces/braces.
        file_path = event.data.strip()
        
        # Specifically for Windows/macOS where the path might be wrapped in {} or quotes
        # It's safer to remove these if present.
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        
        # If multiple files are dropped, we only take the first one
        if ' ' in file_path:
             file_path = file_path.split(' ')[0]

        if os.path.isfile(file_path):
            self.load_image(file_path)
        else:
            print(f"Error: Invalid file path dropped: {file_path}")

    def load_image(self, file_path):
        self.image_path = file_path
        try:
            # Note: PIL needs to keep the image object referenced or it will be garbage collected
            # We open the image and save a reference to it as self.img
            self.img = Image.open(file_path)
            
            # Calculate new size to fit within the label while maintaining aspect ratio
            w, h = self.img.size
            max_w, max_h = self.image_label.winfo_width(), self.image_label.winfo_height()
            
            # If the window is not yet fully rendered, use a default size (e.g., 400x300)
            if max_w == 1 and max_h == 1:
                 max_w, max_h = 400, 300 
            
            ratio = min(max_w / w, max_h / h)
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            
            resized_img = self.img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            self.photo = ImageTk.PhotoImage(resized_img)
            self.image_label.config(image=self.photo, text="")
            self.image_label.image = self.photo # Keep a reference!
            self.root.update_idletasks() # Force update to get accurate dimensions next time

        except Exception as e:
            print(f"Error loading image: {e}")
            self.image_label.config(image=None, text="Error loading image.\nTry another file.")
            self.photo = None
    
    def update_slider_value(self, value):
        self.slider_value.config(text=f"Value: {value}")
    
    def submit(self):
        if not self.image_path:
            print("Error: Please select an image")
            return
        print(f"Image: {self.image_path}")
        print(f"Slider: {self.slider.get()}")
        print(f"Input 1: {self.input1.get()}")
        print(f"Input 2: {self.input2.get()}")

if __name__ == "__main__":
    # *** IMPORTANT CHANGE: Use TkinterDnD.Tk() instead of tk.Tk() ***
    root = TkinterDnD.Tk()
    app = ImageProcessorGUI(root)
    root.mainloop()