import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import webbrowser 
from tkinterdnd2 import DND_ALL, TkinterDnD 

# --- Tooltip Class (Remains the same) ---
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

# --- Main Application Classes (ImageProcessorGUI remains the same) ---

class ImageProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")
        self.root.geometry("500x700")
        
        # --- Variables ---
        self.current_image = None
        self.image_path = None
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
            command=self.show_help,
            relief=tk.FLAT, 
            fg="blue"
        )
        self.how_to_use_button.pack(side=tk.RIGHT)
        
        self.root.after(100, lambda: self.show_tooltip_popup(self.how_to_use_button))

    def show_tooltip_popup(self, widget):
        message = "Click here for instructions or visit the portfolio link!"
        Tooltip(widget, message, delay_ms=4000)

    def show_help(self):
        url = "hub.com/peter00123/portfolio"
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        webbrowser.open_new_tab(url)
        messagebox.showinfo("Portfolio", f"Opening link in your browser:\n{url}")


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
    
    def browse_image(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")])
        if file_path:
            self.load_image(file_path)
    
    def drop_image(self, event):
        file_path = event.data.strip().strip('{}')
        if ' ' in file_path: file_path = file_path.split(' ')[0]
             
        if os.path.isfile(file_path):
            self.load_image(file_path)
        else:
            messagebox.showerror("Error", f"Invalid file path dropped: {file_path}")
    
    def load_image(self, file_path):
        self.image_path = file_path
        try:
            self.current_image = Image.open(file_path)
            max_size = (400, 300)
            preview_img = self.current_image.copy()
            preview_img.thumbnail(max_size)
            self.photo = ImageTk.PhotoImage(preview_img)
            self.image_label.config(image=self.photo, text="")
            self.image_label.image = self.photo
        except Exception as e:
            messagebox.showerror("Error Loading Image", f"Could not load image: {e}")
            self.image_label.config(image=None, text="Error loading image.\nClick to browse.")
            self.current_image = None
    
    def update_slider_value(self, value):
        self.slider_value.config(text=f"Value: {value}")
    
    def submit(self):
        if not self.current_image:
            messagebox.showerror("Error", "Please select an image before submitting.")
            return
            
        resize_dim = self.slider.get()
        try:
            resized_image = self.current_image.resize((resize_dim, resize_dim), Image.Resampling.NEAREST)
            self.main_frame.pack_forget()
            
            self.result_screen = ResultScreen(
                self.root, 
                resized_image, 
                self.go_back_to_main
            )
            self.result_screen.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Processing Error", f"Could not resize image: {e}")
            self.main_frame.pack(fill=tk.BOTH, expand=True)

    def go_back_to_main(self):
        self.result_screen.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        if self.image_path:
             self.load_image(self.image_path)


class ResultScreen(tk.Frame):
    """A separate screen to display the resized image and save/redo buttons."""
    def __init__(self, master, image_to_preview, redo_callback):
        super().__init__(master)
        self.resized_image = image_to_preview
        self.redo_callback = redo_callback
        self.photo = None 
        self.setup_result_screen()

    def setup_result_screen(self):
        tk.Label(self, text="Image Preview (Resized)", font=("Arial", 16, "bold")).pack(pady=10)

        # 1. Calculate and display the scaled-up preview
        preview_width = 300 
        scale_factor = max(1, preview_width // self.resized_image.width)
        
        # Calculate the actual dimensions of the scaled preview image
        display_w = self.resized_image.width * scale_factor
        display_h = self.resized_image.height * scale_factor
        
        display_img = self.resized_image.resize(
            (display_w, display_h), 
            Image.Resampling.NEAREST
        )

        self.photo = ImageTk.PhotoImage(display_img)
        preview_label = tk.Label(self, image=self.photo, text="")
        preview_label.pack(pady=10)
        preview_label.image = self.photo
        
        # --- NEW BOX: Displaying the Preview Image Dimensions ---
        tk.Label(self, text="Preview Box Dimensions:").pack(pady=(10, 0))
        
        # Create a visible box/label to display the preview size
        preview_size_box = tk.Label(
            self, 
            text=f"Length: {display_w} px, Breadth: {display_h} px",
            bg="white", 
            relief=tk.SUNKEN, # Gives the label a 'box' appearance
            padx=10, 
            pady=5,
            font=("Arial", 10)
        )
        preview_size_box.pack(pady=5)
        # --- END NEW BOX ---

        tk.Label(self, text=f"Actual Saved Size: ({self.resized_image.width}x{self.resized_image.height}) px").pack(pady=5)

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
            command=self.download_image,
            bg="blue", fg="white", padx=20, pady=10
        ).pack(side=tk.LEFT, padx=20)

    def download_image(self):
        default_filename = f"resized_{self.resized_image.width}x{self.resized_image.height}.png"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_filename,
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self.resized_image.save(file_path)
                messagebox.showinfo("Success", f"Image successfully saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save image: {e}")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = ImageProcessorGUI(root)
    root.mainloop()