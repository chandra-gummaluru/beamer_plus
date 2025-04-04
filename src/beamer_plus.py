import sys
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import colorchooser
from PIL import Image, ImageTk
import json
import cv2  # For video playback

class PDFViewer:
    def __init__(self, root, pdf_path, slides, durations, videos):
        self.root = root
        self.pdf_doc = fitz.open(pdf_path)
        self.slides = slides
        self.durations = durations
        self.videos = videos  # New video dictionary
        self.current_index = 0
        self.video_player = None  # Placeholder for video player
        self.video_frame_count = 0
        self.current_video_path = None  # To track the current video being played

        self.canvas = tk.Canvas(root, width=800, height=600)  # Set default dimensions
        self.canvas.pack(fill=tk.BOTH, expand=True) 
        
        self.annotations_per_slide = {}

        self.drawing = False
        self.prev_x = None
        self.prev_y = None
        self.pen_color = "black"
        self.pen_size = 2
        self.annotations = []
        self.mode = "normal"

        self.update_image()

        root.bind("<Left>", self.prev_page)
        root.bind("<Right>", self.next_page)
        root.bind("<Configure>", self.update_image)  # Redraw on window resize
        self.canvas.bind("<Configure>", self.on_resize)
        
        self.root.bind("<KeyPress>", self.handle_key_press)
        

        self.auto_advance()

    def handle_key_press(self, event):
        if event.char.lower() == '=':
            if self.pen_size < 10:
                self.pen_size += 1
                self.mode = "draw"
                self.root.config(cursor="pencil")
        if event.char.lower() == '-':
            if self.pen_size > 1:
                self.pen_size -= 1
                self.mode = "draw"
                self.root.config(cursor="pencil")
        if event.char.lower() == 'c':
            self.clear_annotations()
        if event.char.lower() == 'd':
            self.mode = "draw"
            self.root.config(cursor="pencil")
        elif event.char.lower() == 'e':
            self.mode = "erase"
            self.root.config(cursor="circle")
        elif event.char.lower() == 'c':
            self.clear_annotations()
        else:
            self.mode = "normal"
            self.root.config(cursor="")
              

    def update_pen_size(self, size):
        """Update the pen size."""
        self.pen_size = int(size)

    def choose_pen_color(self):
        """Open a color chooser dialog to select the pen color."""
        color_code = colorchooser.askcolor(title="Choose Pen Color")[1]
        if color_code:
            self.pen_color = color_code

    def toggle_erase(self):
        """Toggle between drawing and erasing modes."""
        self.drawing = False
        self.canvas.bind("<Button-1>", self.erase_annotation)

    def erase_annotation(self, event):
        """Erase annotations on the canvas."""
        if self.prev_x and self.prev_y:
            x, y = event.x, event.y
            self.canvas.create_oval(x - self.pen_size, y - self.pen_size, x + self.pen_size, y + self.pen_size, outline="white", fill="white")
            self.annotations = [anno for anno in self.annotations if not self.is_near(anno, x, y)]
        self.prev_x = event.x
        self.prev_y = event.y

    def is_near(self, annotation, x, y):
        """Check if an annotation is near a given (x, y) point."""
        ax, ay, _, _ = annotation
        return abs(ax - x) < self.pen_size * 2 and abs(ay - y) < self.pen_size * 2

    def draw(self, event):
        if self.mode == "draw":
            x, y = event.x, event.y
            if self.prev_x is not None and self.prev_y is not None:
                self.canvas.create_line(self.prev_x, self.prev_y, x, y, fill=self.pen_color, width=self.pen_size, capstyle=tk.ROUND, smooth=tk.TRUE)
            
            slide_num = self.slides[self.current_index]
            if slide_num not in self.annotations_per_slide:
                self.annotations_per_slide[slide_num] = []
            self.annotations_per_slide[slide_num].append((self.prev_x, self.prev_y, x, y, self.pen_size, self.pen_color))

            self.prev_x, self.prev_y = x, y  # Update previous coordinates


    def clear_annotations(self):
        """Clear annotations only for the current slide."""
        slide_num = self.slides[self.current_index]
        self.canvas.delete("all")
        if slide_num in self.annotations_per_slide:
            del self.annotations_per_slide[slide_num]  # Remove stored annotations
        self.update_image()  # Redraw slide without annotations

    def update_image(self, event=None):
        """Update the canvas based on the current slide and redraw stored annotations."""
        if self.current_index < len(self.slides):
            slide_num = self.slides[self.current_index]
            slide_key = 's' + str(slide_num)

            if slide_key in self.videos:
                self.open_video(self.videos[slide_key])
                self.play_video()
            else:
                self.display_pdf_slide(slide_num)
                self.restore_annotations(slide_num)  # Restore previous annotations

    def restore_annotations(self, slide_num):
        """Redraw stored annotations when returning to a slide."""
        if slide_num in self.annotations_per_slide:
            for x, y, pen_size, pen_color in self.annotations_per_slide[slide_num]:
                self.canvas.create_oval(x - pen_size, y - pen_size, x + pen_size, y + pen_size,
                                        outline=pen_color, fill=pen_color)


    def display_pdf_slide(self, slide_num):
        """Render and display a PDF slide on the canvas."""
        page_num = slide_num - 1  # Convert to zero-based index
        page = self.pdf_doc[page_num]
        zoom_factor = 10.0  # Render at double resolution for better clarity
        mat = fitz.Matrix(zoom_factor, zoom_factor)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Get canvas size with minimum fallback
        canvas_width = max(self.canvas.winfo_width(), 800)
        canvas_height = max(self.canvas.winfo_height(), 600)

        # Scale while maintaining aspect ratio
        aspect_ratio = pix.width / pix.height
        if canvas_width / aspect_ratio <= canvas_height:
            new_width = canvas_width
            new_height = int(canvas_width / aspect_ratio)
        else:
            new_height = canvas_height
            new_width = int(canvas_height * aspect_ratio)

        img = img.resize((new_width, new_height), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(img)

        # Clear canvas and display the image
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width//2, canvas_height//2, anchor=tk.CENTER, image=self.tk_img)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        # Bind drawing event (for pen)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", lambda event: self.set_drawing(False))
        self.canvas.bind("<Button-1>", lambda event: self.set_drawing(True))

    def set_drawing(self, drawing):
        self.drawing = drawing
        if not drawing:
            self.prev_x, self.prev_y = None, None


    def open_video(self, video_info):
        video_path = video_info["path"]
        self.video_player = cv2.VideoCapture(video_path)
        self.video_frame_count = int(self.video_player.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_fps = int(video_info["fps"])
        if not self.video_player.isOpened():
            print(f"Error: Could not open video file at {video_path}")
            return

    def play_video(self, frame_index = 0):
        if frame_index >= self.video_frame_count:
            print("Done")
            return
        ret, frame = self.video_player.read()
        if not ret:
            print("Error: Failed to read a frame from the video.")
            return
        
        # Resize and update the frame on the canvas
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = self.resize_frame(frame, self.canvas.winfo_width(), self.canvas.winfo_height())
        frame_image = Image.fromarray(frame_resized)
        frame_image = ImageTk.PhotoImage(frame_image)

        # Keep a reference to avoid garbage collection
        self.current_frame = frame_image

        # Show the resized video frame on the canvas
        self.canvas.delete("all")
        self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, anchor=tk.CENTER, image=frame_image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        # Continue playing the video
        self.root.after(1000//self.video_fps, self.play_video, frame_index+1)  # 40 ms (25 FPS)


    def next_page(self, event=None):
        """Move to the next slide."""
        if self.current_index < len(self.slides) - 1:
            self.current_index += 1
            self.update_image()
            self.auto_advance()

    def prev_page(self, event=None):
        """Move to the previous slide."""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_image()

    def auto_advance(self):
        """Automatically advance slides based on their duration."""
        slide_num = self.slides[self.current_index]
        duration = self.durations.get('s' + str(slide_num), None)
        if duration is not None:
            self.root.after(int(duration), self.next_page)

    def on_resize(self, event):
        """Resize video frame if necessary when the window size changes."""
        canvas_width = event.width
        canvas_height = event.height

        if self.video_player and self.video_player.isOpened():
            ret, frame = self.video_player.read()
            if ret:
                frame_resized = self.resize_frame(frame, canvas_width, canvas_height)
                frame_image = Image.fromarray(frame_resized)
                frame_image = ImageTk.PhotoImage(frame_image)

                self.canvas.delete("all")
                self.canvas.create_image(canvas_width // 2, canvas_height // 2, anchor=tk.CENTER, image=frame_image)
                self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

                # Continue playing the video
                self.root.after(40, self.display_video_frame)

    def resize_frame(self, frame, canvas_width, canvas_height):
        """Resize the video frame to fit the canvas while maintaining aspect ratio."""
        video_height, video_width = frame.shape[:2]
        aspect_ratio = video_width / video_height

        if canvas_width / canvas_height > aspect_ratio:
            new_height = canvas_height
            new_width = int(canvas_height * aspect_ratio)
        else:
            new_width = canvas_width
            new_height = int(canvas_width / aspect_ratio)

        return cv2.resize(frame, (new_width, new_height))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python presenter.py <pdf_path> <config.json>")
    
    config_path = sys.argv[1]

    with open(config_path, "r") as config_file:
        config = json.load(config_file)
    
    pdf_path = config.get("pdf", "")
    slides = config.get("slides", [])
    durations = config.get("durations", {})
    videos = config.get("videos", {})

    if len(slides) == 0:
        sys.exit("Error: 'slides' list cannot be empty")

    root = tk.Tk()
    root.title("Beamer+")

    viewer = PDFViewer(root, pdf_path, slides, durations, videos)
    root.mainloop()
