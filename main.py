import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
# New import for Drag-and-Drop functionality
# Import the main class and constant from the installed package
from tkinterdnd2 import TkinterDnD, DND_ALL

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