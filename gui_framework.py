# gui_framework.py
import tkinter as tk
import os
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from tkinterdnd2 import DND_ALL, TkinterDnD 
from image_logic import ImageProcessorLogic # Import the logic class

# --- Tooltip Class (Remains the same, kept in GUI file as it's UI specific) ---
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
        self.root.title("Image Processor")
        self.root.geometry("500x700")
        
        # Instantiate the Logic Handler
        self.logic = ImageProcessorLogic() 

        # --- Variables ---
        self.photo = None
        
        # --- Top Bar for the 'How to Use' Button ---
        self.top_bar = tk.Frame(root, height=30)
        self.top_bar.pack(fill=tk.X, padx=10, pady=(5, 0))
        self.setup_top_bar(self.top_bar)
        
        # --- Setup Main Container ---
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_main_screen(self.main_frame)
        
    def setup_top_bar(self, frame):
        tk.Label(frame).pack(side=tk.LEFT, expand=True) 

        self.how_to_use_button = tk.Button(
            frame, 
            text="ⓘ How to Use", 
            command=self.logic.open_portfolio_link, # Calls logic method
            relief=tk.FLAT, 
            fg="blue"
        )
        self.how_to_use_button.pack(side=tk.RIGHT)
        
        self.root.after(100, lambda: self.show_tooltip_popup(self.how_to_use_button))

    def show_tooltip_popup(self, widget):
        message = "Click here for instructions or visit the portfolio link!"
        Tooltip(widget, message, delay_ms=4000)

    def setup_main_screen(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

        self.image_label = tk.Label(
            frame, text="Drag & Drop Image Here\nor Click to Browse",
            bg="lightgray", height=10, width=50
        )
        self.image_label.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.image_label.bind("<Button-1>", self.browse_image)
        
        self.image_label.drop_target_register(DND_ALL) 
        self.image_label.dnd_bind('<<Drop>>', self.drop_image) 
        
        tk.Button(frame, text="Browse Image", command=self.browse_image).pack(pady=5)
        
        tk.Label(frame, text="Resize Dimension (10 to 200 pixels):").pack()
        self.slider = tk.Scale(
            frame, from_=10, to=200, orient=tk.HORIZONTAL, length=300, 
            resolution=1
        )
        self.slider.set(50)
        self.slider.pack(pady=5, padx=10, fill=tk.X)
        self.slider_value = tk.Label(frame, text="Value: 50")
        self.slider_value.pack()
        self.slider.config(command=self.update_slider_value)
        
        tk.Button(frame, text="Submit & Resize", command=self.submit, bg="green", fg="white").pack(pady=20)
    
    # --- Image Loading Handlers (UI-to-Logic bridge) ---
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
        """Calls logic to load image and updates the UI."""
        try:
            preview_img, _ = self.logic.load_image(file_path)
            
            # Convert PIL image for Tkinter display
            self.photo = ImageTk.PhotoImage(preview_img)
            self.image_label.config(image=self.photo, text="")
            self.image_label.image = self.photo
        except Exception as e:
            messagebox.showerror("Error Loading Image", f"Could not load image: {e}")
            self.image_label.config(image=None, text="Error loading image.\nClick to browse.")
            self.logic.current_image = None
    
    def update_slider_value(self, value):
        self.slider_value.config(text=f"Value: {value}")
    
    def submit(self):
        if not self.logic.current_image:
            messagebox.showerror("Error", "Please select an image before submitting.")
            return
            
        resize_dim = self.slider.get()
        try:
            # Call logic to process the image and calculate UI dimensions
            resized_image, display_w, display_h, text_w, text_h = self.logic.process_and_resize(resize_dim)
            
            self.main_frame.pack_forget()
            
            self.result_screen = ResultScreen(
                self.root, 
                self.logic, # Pass the logic instance
                resized_image, 
                display_w, display_h, text_w, text_h,
                self.go_back_to_main
            )
            self.result_screen.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Processing Error", f"Could not resize image: {e}")
            self.main_frame.pack(fill=tk.BOTH, expand=True)

    def go_back_to_main(self):
        self.result_screen.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        # Reload the original preview image if available
        if self.logic.image_path:
             self._display_loaded_image(self.logic.image_path)


class ResultScreen(tk.Frame):
    """A separate screen to display the resized image and save/redo buttons."""
    def __init__(self, master, logic, resized_image, display_w, display_h, text_w, text_h, redo_callback):
        super().__init__(master)
        self.logic = logic # Store the logic instance
        self.resized_image = resized_image
        self.display_w = display_w
        self.display_h = display_h
        self.text_w = text_w
        self.text_h = text_h
        self.redo_callback = redo_callback
        self.photo = None 
        self.setup_result_screen()
        
    def copy_text(self):
        """Copies the content of the text widget using Tkinter's clipboard functions."""
        try:
            text_to_copy = self.text_output.get("1.0", tk.END).strip()
            
            # Tkinter clipboard commands
            self.clipboard_clear()
            self.clipboard_append(text_to_copy)
            messagebox.showinfo("Copied", "Text content copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Copy Error", f"Could not copy text: {e}")

    def download_image(self):
        """Calls logic to save the image."""
        try:
            self.logic.save_image(self.resized_image)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save image: {e}")


    def setup_result_screen(self):
        center_frame = tk.Frame(self)
        center_frame.pack(pady=10)

        tk.Label(center_frame, text="Image Preview (Resized)", font=("Arial", 16, "bold")).pack(pady=10)

        # 1. Display the scaled-up preview
        display_img = self.resized_image.resize(
            (self.display_w, self.display_h), 
            Image.Resampling.NEAREST
        )

        self.photo = ImageTk.PhotoImage(display_img)
        preview_label = tk.Label(center_frame, image=self.photo, text="", width=self.display_w, height=self.display_h)
        preview_label.pack(pady=5)
        preview_label.image = self.photo
        
        
        # --- TEXT OUTPUT BOX & COPY BUTTON ---
        text_control_frame = tk.Frame(center_frame)
        text_control_frame.pack(pady=(10, 0))

        tk.Label(text_control_frame, text="Text Output (Placeholder):").pack(side=tk.LEFT)
        
        # New Copy Button
        tk.Button(
            text_control_frame, 
            text="Copy Text", 
            command=self.copy_text,
            bg="#e0e0e0"
        ).pack(side=tk.LEFT, padx=10)

        self.text_output = tk.Text(
            center_frame, 
            wrap=tk.WORD, 
            width=self.text_w, 
            height=self.text_h,
            bg="#f0f0f0",
            relief=tk.SUNKEN
        )
        self.text_output.pack(pady=5)
        
        # Placeholder text
        self.text_output.insert(tk.END, 
            f"This text box is approximately {self.text_w} characters wide and {self.text_h} lines high, matching the preview image size.\n\n"
            "This is where the QR code text output would go."
        )
        # --- END TEXT OUTPUT BOX & COPY BUTTON ---
        
        # Previous info box for dimensions (kept for completeness)
        tk.Label(center_frame, text="Preview Area Dimensions:").pack(pady=(10, 0))
        preview_size_box = tk.Label(
            center_frame, 
            text=f"Width: {self.display_w} px, Height: {self.display_h} px",
            bg="white", 
            relief=tk.SUNKEN, 
            padx=10, 
            pady=5,
            font=("Arial", 10)
        )
        preview_size_box.pack(pady=5)

        tk.Label(center_frame, text=f"Actual Saved Size: ({self.resized_image.width}x{self.resized_image.height}) px").pack(pady=5)

        # 2. Button Frame
        button_frame = tk.Frame(self)
        button_frame.pack(pady=30)

        tk.Button(
            button_frame, 
            text="Redo (Go Back)", 
            command=self.redo_callback,
            bg="orange", fg="white", padx=20, pady=10
        ).pack(side=tk.LEFT, padx=20)

        tk.Button(
            button_frame, 
            text="Download & Save", 
            command=self.download_image, # Calls the ResultScreen method, which calls logic
            bg="blue", fg="white", padx=20, pady=10
        ).pack(side=tk.LEFT, padx=20)