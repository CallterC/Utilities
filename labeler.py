import os
import shutil
from tkinter import Tk, Label, Frame, Button, StringVar, messagebox, Entry
from tkinter import ttk
from PIL import Image, ImageTk

class BatchImageLabeler:
    def __init__(self, root, image_folder, initial_labels):
        self.root = root
        self.image_folder = image_folder
        self.labels = initial_labels.copy()
        self.selected_images = set()
        self.current_batch = []
        self.thumbnail_size = (200, 200)

        self.last_selected_index = None  # Track for shift selection

        # Create label folders
        for label in self.labels:
            os.makedirs(os.path.join(image_folder, label), exist_ok=True)

        # GUI setup
        self.grid_frame = Frame(root)
        self.grid_frame.pack()

        # Label management frame
        label_frame = Frame(root)
        label_frame.pack(pady=20)

        # Combobox for labels with scrolling
        self.label_var = StringVar()
        self.label_combobox = ttk.Combobox(
            label_frame, 
            textvariable=self.label_var,
            values=self.labels,
            state="readonly",
            width=15
        )
        self.label_combobox.pack(side="left", padx=20)
        
        # Bind mouse wheel to combobox dropdown
        self.label_combobox.bind("<<ComboboxSelected>>", lambda e: self.root.focus())
        self.label_combobox.bind("<MouseWheel>", self.scroll_labels)

        # New label entry
        self.new_label_entry = Entry(label_frame, width=15)
        self.new_label_entry.pack(side="left", padx=5)

        # Add label button
        Button(label_frame, text="+ Add Label", command=self.add_new_label).pack(side="left", padx=5)

        # Apply label button
        Button(root, text="Apply Label to Selected", command=self.apply_label).pack(pady=5)

        self.load_next_batch()

    def toggle_selection(self, event, index):
        """Handle selection with Ctrl/Shift support"""
        current_state = event.state
        ctrl_pressed = (current_state & 0x4) != 0  # Check Control key (Linux/Windows)
        shift_pressed = (current_state & 0x1) != 0  # Check Shift key
        
        # Handle macOS modifier keys (different bitmask)
        if 'darwin' in os.sys.platform:
            ctrl_pressed = (current_state & 0x40000) != 0  # Command key
            shift_pressed = (current_state & 0x2) != 0

        if shift_pressed and self.last_selected_index is not None:
            # Select range between last selected and current
            start = min(self.last_selected_index, index)
            end = max(self.last_selected_index, index)
            self.selected_images.update(range(start, end + 1))
            
            # Highlight all in range
            for i in range(start, end + 1):
                self.highlight_image(i, True)
        elif ctrl_pressed:
            # Toggle single selection
            if index in self.selected_images:
                self.selected_images.remove(index)
                self.highlight_image(index, False)
            else:
                self.selected_images.add(index)
                self.highlight_image(index, True)
            self.last_selected_index = index
        else:
            # Clear selection and select single item
            self.selected_images.clear()
            for i in range(len(self.current_batch)):
                self.highlight_image(i, False)
            self.selected_images.add(index)
            self.highlight_image(index, True)
            self.last_selected_index = index

    def highlight_image(self, index, selected):
        """Update visual state of image thumbnail"""
        widget = self.grid_frame.grid_slaves(row=index//10, column=index%10)[0]
        if selected:
            widget.config(borderwidth=3, relief="solid", highlightbackground="blue")
        else:
            widget.config(borderwidth=0, relief="flat")

    def scroll_labels(self, event):
        """Scroll through combobox options with mouse wheel"""
        values = self.label_combobox["values"]
        if not values:
            return
        
        current_index = self.label_combobox.current()
        if event.delta > 0:  # Scroll up
            new_index = max(0, current_index - 1)
        else:  # Scroll down
            new_index = min(len(values)-1, current_index + 1)
        
        self.label_combobox.current(new_index)
        self.label_var.set(values[new_index])

    def add_new_label(self):
        new_label = self.new_label_entry.get().strip()
        if not new_label:
            messagebox.showwarning("Empty Label", "Please enter a label name")
            return
        if new_label in self.labels:
            messagebox.showwarning("Duplicate Label", f"'{new_label}' already exists!")
            return

        # Add to labels and create folder
        self.labels.append(new_label)
        os.makedirs(os.path.join(self.image_folder, new_label), exist_ok=True)
        
        # Update dropdown menu
        self.update_label_dropdown()
        self.new_label_entry.delete(0, 'end')
        messagebox.showinfo("Success", f"Label '{new_label}' added!")

    def update_label_dropdown(self):
        # Destroy old dropdown and create new one
        self.label_dropdown.destroy()
        self.label_dropdown = OptionMenu(self.root, self.label_var, *self.labels)
        self.label_dropdown.pack(side="left", padx=5)

    # ... (keep previous methods load_next_batch, toggle_selection, apply_label unchanged) ...

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
        self.current_batch = all_files[:50]  # Get next 30 images

        # Display images in a 5x6 grid
        for idx, filename in enumerate(self.current_batch):
            row, col = divmod(idx, 10)
            try:
                img_path = os.path.join(self.image_folder, filename)
                img = Image.open(img_path)
                img.thumbnail(self.thumbnail_size)
                photo = ImageTk.PhotoImage(img)
                
                lbl = Label(self.grid_frame, image=photo, borderwidth=0)
                lbl.image = photo  # Keep reference to avoid garbage collection
                lbl.grid(row=row, column=col, padx=5, pady=5)
                
                # Bind click event to toggle selection
                lbl.bind("<Button-1>", lambda e, i=idx: self.toggle_selection(e, i))
            except Exception as e:
                print(f"Error loading {filename}: {e}")

        if not self.current_batch:
            Label(self.grid_frame, text="All images labeled! 🎉").grid(row=0, column=0)

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
    root.title("Batch Image Labeler with Dynamic Labels")
    
    # Configure your settings here
    IMAGE_FOLDER = "/path/to/your/photos"
    INITIAL_LABELS = ["cat", "dog", "bird"]  # Starting labels
    
    app = BatchImageLabeler(root, IMAGE_FOLDER, INITIAL_LABELS)
    root.mainloop()
