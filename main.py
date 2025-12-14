# main_app.py
from tkinterdnd2 import TkinterDnD
from gui_framework import ImageProcessorGUI
import os

def main():
    """Initializes the Tkinter root and starts the application."""
    # Use TkinterDnD.Tk() for drag-and-drop support
    root = TkinterDnD.Tk()
    app = ImageProcessorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()