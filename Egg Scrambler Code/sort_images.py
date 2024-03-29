# -*- coding: utf-8 -*-
"""
Created on Sun Mar 17 19:31:24 2024

@author: 20Jan
"""

import os
import shutil
from tkinter import Tk, Canvas, Button, Frame, messagebox
from PIL import Image, ImageTk, ImageOps

class ImageSlideshow:
    def __init__(self, master, image_folder, folder_a, folder_b):
        self.master = master
        self.image_folder = image_folder
        self.folder_a = folder_a
        self.folder_b = folder_b
        self.current_image_id = None  # Track the current image displayed on the canvas
        self.image_files = [f for f in os.listdir(image_folder) if f.endswith(('png', 'jpg', 'jpeg', 'gif'))]
        self.photos = []
        self.image_index = 0

        if not self.image_files:
            messagebox.showerror("Error", "No images found in the directory.")
            self.master.destroy()
            return
        
        # Define a fixed size for the image display area
        self.image_display_width = 800
        self.image_display_height = 600
        
        # Create a canvas for the image within the image frame
        self.image_frame = Frame(master, width=self.image_display_width, height=self.image_display_height)
        self.image_frame.pack_propagate(False)  # Prevent the frame from resizing to fit the image
        self.image_frame.pack()
        
        self.canvas = Canvas(self.image_frame, width=self.image_display_width, height=self.image_display_height)
        self.canvas.pack(fill="both", expand=True)
        
        # Buttons frame
        self.buttons_frame = Frame(master)
        self.buttons_frame.pack(fill='x', pady=10)

        # Define buttons
        self.btn_folder_a = Button(self.buttons_frame, text="Move to Cooked Folder", command=lambda: self.move_image('a'))
        self.btn_folder_a.pack(side='left', expand=True, padx=5)

        self.btn_folder_b = Button(self.buttons_frame, text="Move to Uncooked Folder", command=lambda: self.move_image('b'))
        self.btn_folder_b.pack(side='left', expand=True, padx=5)

        self.btn_delete = Button(self.buttons_frame, text="Delete Image", command=self.delete_image)
        self.btn_delete.pack(side='right', expand=True, padx=5)

        self.preload_images()
        self.show_image()

    def preload_images(self):
        for filename in self.image_files:
            image_path = os.path.join(self.image_folder, filename)
            img = Image.open(image_path)
            # Resize the image to fit within the fixed display area, preserving aspect ratio
            img = ImageOps.contain(img, (self.image_display_width, self.image_display_height))
            self.photos.append(ImageTk.PhotoImage(img))

    def show_image(self):
        if self.image_index < len(self.photos):
            if self.current_image_id is not None:
                self.canvas.delete(self.current_image_id)  # Clear the previous image
            self.current_image_id = self.canvas.create_image(self.image_display_width // 2, self.image_display_height // 2,
                                     image=self.photos[self.image_index], anchor='center')
        else:
            messagebox.showinfo("End", "No more images.")
            self.master.destroy()

    def move_image(self, folder):
        if self.image_index < len(self.image_files):
            current_image = self.image_files[self.image_index]
            src_path = os.path.join(self.image_folder, current_image)
            dest_path = os.path.join(self.folder_a if folder == 'a' else self.folder_b, current_image)
            shutil.move(src_path, dest_path)
            self.goto_next_image()

    def delete_image(self):
        if self.image_index < len(self.image_files):
            src_path = os.path.join(self.image_folder, self.image_files[self.image_index])
            os.remove(src_path)
            self.goto_next_image()

    def goto_next_image(self):
        self.image_index += 1
        if self.image_index < len(self.photos):
            self.show_image()
        else:
            messagebox.showinfo("End", "No more images.")
            self.master.destroy()

if __name__ == "__main__":
    root = Tk()
    root.title("Image Slideshow")
    
    # Set the directory of your images
    IMAGE_FOLDER = "downloaded_images"
    # Set the target directories for the two buttons
    FOLDER_A = "eggs_dataset/cooked"
    FOLDER_B = "eggs_dataset/uncooked"
    
    # Create directories if they don't exist
    os.makedirs(FOLDER_A, exist_ok=True)
    os.makedirs(FOLDER_B, exist_ok=True)

    app = ImageSlideshow(root, IMAGE_FOLDER, FOLDER_A, FOLDER_B)
    root.mainloop()