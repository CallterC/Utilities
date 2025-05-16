import os
import shutil
from tkinter import Tk, Label, Frame, Button, StringVar, OptionMenu, messagebox
from PIL import Image, ImageTk

class BatchImageLabeler:
    def __init__(self, root, image_folder, labels):
        self.root = root
        self.image_folder = image_folder
        self.labels = labels
        self.selected_images = set()  # Track selected photo indices
        self.current_batch = []  # Store filenames of current 30 photos
        self.thumbnail_size = (250, 250)  # Adjust thumbnail size

        # Create label folders if they don't exist
        for label in self.labels:
            os.makedirs(os.path.join(image_folder, label), exist_ok=True)

        # GUI setup
        self.grid_frame = Frame(root)
        self.grid_frame.pack()

        # Label selection dropdown
        self.label_var = StringVar(root)
        self.label_dropdown = OptionMenu(root, self.label_var, *self.labels)
        self.label_dropdown.pack(pady=10)

        # Apply label button
        self.apply_btn = Button(root, text="Apply Label to Selected", command=self.apply_label)
        self.apply_btn.pack(pady=5)

        # Load first batch
        self.load_next_batch()

    def load_next_batch(self):
        # Clear current grid and selection
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.selected_images.clear()

        # Scan folder for remaining images (ignoring subfolders)
        all_files = [
            f for f in os.listdir(self.image_folder)
            if os.path.isfile(os.path.join(self.image_folder, f)) 
            and f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ]
        self.current_batch = all_files[:30]  # Get next 30 images

        # Display images in a 5x6 grid
        for idx, filename in enumerate(self.current_batch):
            row, col = divmod(idx, 6)
            try:
                img_path = os.path.join(self.image_folder, filename)
                img = Image.open(img_path)
                img.thumbnail(self.thumbnail_size)
                photo = ImageTk.PhotoImage(img)
                
                lbl = Label(self.grid_frame, image=photo, borderwidth=0)
                lbl.image = photo  # Keep reference to avoid garbage collection
                lbl.grid(row=row, column=col, padx=5, pady=5)
                
                # Bind click event to toggle selection
                lbl.bind("<Button-1>", lambda e, i=idx: self.toggle_selection(i))
            except Exception as e:
                print(f"Error loading {filename}: {e}")

        if not self.current_batch:
            Label(self.grid_frame, text="All images labeled! 🎉").grid(row=0, column=0)

    def toggle_selection(self, index):
        if index in self.selected_images:
            self.selected_images.remove(index)
            self.grid_frame.grid_slaves(row=index//6, column=index%6)[0].config(borderwidth=0)
        else:
            self.selected_images.add(index)
            self.grid_frame.grid_slaves(row=index//6, column=index%6)[0].config(borderwidth=3, relief="solid")

    def apply_label(self):
        if not self.selected_images:
            messagebox.showwarning("No Selection", "Select photos first!")
            return
        if not self.label_var.get():
            messagebox.showwarning("No Label", "Choose a label from the dropdown!")
            return

        # Move selected files to their label folder
        label_dir = os.path.join(self.image_folder, self.label_var.get())
        for idx in self.selected_images:
            src = os.path.join(self.image_folder, self.current_batch[idx])
            shutil.move(src, label_dir)

        # Reload grid with next batch
        self.load_next_batch()

if __name__ == "__main__":
    root = Tk()
    root.title("Batch Image Labeler")
    
    # Configure your settings here
    IMAGE_FOLDER = ""  # ⚠️ TODO: Replace with your folder path
    LABELS = []  # 🏷️ TODO: Your custom labels
    
    app = BatchImageLabeler(root, IMAGE_FOLDER, LABELS)
    root.mainloop()
