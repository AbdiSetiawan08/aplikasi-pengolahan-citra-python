# Aplikasi Pengolahan Citra Digital - Versi Sederhana (Improved)
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys

# Check dan import dependencies dengan error handling
try:
    from PIL import Image, ImageTk
    import cv2
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except ImportError as e:
    print(f"Error: {e}")
    print("Install dependencies dengan: pip install opencv-python pillow numpy matplotlib")
    sys.exit(1)

class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.setup_styles()
        self.setup_ui()
        
    def setup_window(self):
        """Setup main window"""
        self.root.title("🎨 Digital Image Processing Studio - Simplified")
        self.root.geometry("1600x900")
        self.root.configure(bg="#1a1a2e")
        self.root.minsize(1400, 800)
        
    def setup_variables(self):
        """Initialize variables"""
        self.original_image = None
        self.processed_image = None
        self.image_path = None
        self.threshold_var = tk.IntVar(value=128)
        self.division_var = tk.DoubleVar(value=2.0)
        
    def setup_styles(self):
        """Setup modern dark theme styles"""
        self.colors = {
            'bg_primary': '#1a1a2e',
            'bg_secondary': '#16213e',
            'bg_card': '#0f3460',
            'accent': '#e94560',
            'accent_hover': '#ff6b7d',
            'text_primary': '#ffffff',
            'text_secondary': '#a8b2d1',
            'success': '#00d2d3',
            'warning': '#ffa726',
            'button_hover': '#533483',
            'input_bg': '#2d3748',
            'input_focus': '#4a5568'
        }
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure notebook style with larger tabs
        style.configure('Dark.TNotebook', 
                       background=self.colors['bg_primary'],
                       borderwidth=0)
        style.configure('Dark.TNotebook.Tab',
                       background=self.colors['bg_card'],
                       foreground=self.colors['text_primary'],
                       padding=[18, 12],
                       font=('Segoe UI', 10, 'bold'))
        style.map('Dark.TNotebook.Tab',
                 background=[('selected', self.colors['accent'])])
        
    def setup_ui(self):
        """Setup main UI"""
        # Header
        self.create_header()
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Create paned window
        paned_window = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL,
                                     bg=self.colors['bg_primary'], 
                                     sashwidth=6, sashrelief='flat')
        paned_window.pack(fill='both', expand=True)
        
        # Left panel - Controls (larger and more readable)
        left_panel = self.create_control_panel()
        paned_window.add(left_panel, minsize=420)
        
        # Right panel - Images
        right_panel = self.create_image_panel()
        paned_window.add(right_panel, minsize=900)
        
        # Status bar
        self.create_status_bar()
        
    def create_header(self):
        """Create header"""
        header = tk.Frame(self.root, bg=self.colors['accent'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="🎨 DIGITAL IMAGE PROCESSING - SIMPLIFIED",
                font=('Segoe UI', 16, 'bold'),
                bg=self.colors['accent'], fg='white').pack(pady=18)
        
    def create_control_panel(self):
        """Create control panel with enhanced scrolling"""
        panel = tk.Frame(self.root, bg=self.colors['bg_secondary'])
        
        # Main container for scrollable content
        main_container = tk.Frame(panel, bg=self.colors['bg_secondary'])
        main_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Canvas with scrollbar
        canvas = tk.Canvas(main_container, bg=self.colors['bg_secondary'], 
                          highlightthickness=0, bd=0)
        
        # Scrollbar styling
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        
        # Scrollable frame
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_secondary'])
        
        # Configure scroll region
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            
        def configure_canvas(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        
        scrollable_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", configure_canvas)
        
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enhanced mouse wheel scrolling
        def _on_mousewheel(event):
            if event.widget.winfo_exists():
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
        def unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            
        canvas.bind('<Enter>', bind_mousewheel)
        canvas.bind('<Leave>', unbind_mousewheel)
        
        # File Operations
        self.add_section(scrollable_frame, "📁 FILE OPERATIONS", [
            ("📂 Load Image", self.load_image, self.colors['accent']),
            ("💾 Save Result", self.save_image, self.colors['success']),
            ("🔄 Reset", self.reset_image, self.colors['warning'])
        ])
        
        # Basic Operations
        self.add_section(scrollable_frame, "🎛️ BASIC OPERATIONS", [
            ("⚫ Grayscale", self.convert_grayscale, self.colors['bg_card']),
            ("🔲 Binary", self.convert_binary, '#2d3748'),
            ("🔧 Logical NOT", self.logical_not, '#8b5cf6')
        ])
        
        # Arithmetic Division Section (Improved)
        self.add_division_section(scrollable_frame)
        
        # Histogram
        self.add_section(scrollable_frame, "📊 HISTOGRAM", [
            ("📈 Show Histogram", self.show_histogram, '#ef4444')
        ])
        
        # Convolution
        self.add_section(scrollable_frame, "🌊 CONVOLUTION", [
            ("🌊 Gaussian Blur", self.gaussian_blur, '#06b6d4'),
            ("🎯 Sharpen", self.sharpen_image, '#ef4444')
        ])
        
        # Morphology
        self.add_section(scrollable_frame, "🔄 MORPHOLOGY", [
            ("🔴 Erosion (Square)", self.erosion_square, '#dc2626'),
            ("🟢 Erosion (Cross)", self.erosion_cross, '#16a34a')
        ])
        
        # Image info
        self.add_info_section(scrollable_frame)
        
        return panel
        
    def add_section(self, parent, title, buttons):
        """Add a section with larger, more readable buttons"""
        header = tk.Frame(parent, bg=self.colors['accent'], height=40)
        header.pack(fill='x', padx=12, pady=(12, 0))
        header.pack_propagate(False)
        
        tk.Label(header, text=title, font=('Segoe UI', 11, 'bold'),
                bg=self.colors['accent'], fg='white').pack(pady=10)
        
        container = tk.Frame(parent, bg=self.colors['bg_secondary'])
        container.pack(fill='x', padx=12, pady=(0, 8))
        
        for text, command, color in buttons:
            btn = self.create_button(container, text, command, color)
            btn.pack(fill='x', pady=2)
            
    def add_division_section(self, parent):
        """Add improved division operation section with larger text"""
        header = tk.Frame(parent, bg=self.colors['accent'], height=40)
        header.pack(fill='x', padx=12, pady=(12, 0))
        header.pack_propagate(False)
        
        tk.Label(header, text="➗ ARITHMETIC DIVISION", font=('Segoe UI', 11, 'bold'),
                bg=self.colors['accent'], fg='white').pack(pady=10)
        
        container = tk.Frame(parent, bg=self.colors['bg_card'])
        container.pack(fill='x', padx=12, pady=(0, 8))
        
        # Division value input (Enhanced with larger text)
        input_frame = tk.Frame(container, bg=self.colors['bg_card'])
        input_frame.pack(fill='x', padx=15, pady=12)
        
        # Label and Entry in same row
        top_frame = tk.Frame(input_frame, bg=self.colors['bg_card'])
        top_frame.pack(fill='x', pady=(0, 8))
        
        tk.Label(top_frame, text="Division Value (1.0 - 10.0):", 
                font=('Segoe UI', 10, 'bold'),
                bg=self.colors['bg_card'], fg=self.colors['text_primary']).pack(anchor='w')
        
        # Entry field for division value
        entry_frame = tk.Frame(input_frame, bg=self.colors['bg_card'])
        entry_frame.pack(fill='x')
        
        self.division_entry = tk.Entry(entry_frame, 
                                     textvariable=self.division_var,
                                     font=('Segoe UI', 11, 'bold'),
                                     bg=self.colors['input_bg'], 
                                     fg=self.colors['text_primary'],
                                     insertbackground=self.colors['text_primary'],
                                     relief='flat', bd=1, width=12,
                                     justify='center')
        self.division_entry.pack(side='left', padx=(0, 10), ipady=4)
        
        # Apply button with larger size
        apply_btn = tk.Button(entry_frame, text="Apply Division", 
                            command=self.apply_division,
                            font=('Segoe UI', 10, 'bold'),
                            bg=self.colors['success'], fg='white',
                            relief='flat', cursor='hand2',
                            padx=18, pady=8, bd=0)
        apply_btn.pack(side='left')
        
        # Validation
        self.division_entry.bind('<KeyRelease>', self.validate_division_input)
        self.division_entry.bind('<Return>', lambda e: self.apply_division())
        
        # Hover effects for apply button
        def on_enter(e): apply_btn.config(bg='#00a8a9')
        def on_leave(e): apply_btn.config(bg=self.colors['success'])
        apply_btn.bind("<Enter>", on_enter)
        apply_btn.bind("<Leave>", on_leave)
        
    def validate_division_input(self, event=None):
        """Validate division input"""
        try:
            value = float(self.division_entry.get())
            if 1.0 <= value <= 10.0:
                self.division_entry.config(bg=self.colors['input_bg'])
                return True
            else:
                self.division_entry.config(bg='#8b2635')
                return False
        except ValueError:
            self.division_entry.config(bg='#8b2635')
            return False
            
    def apply_division(self):
        """Apply division operation"""
        if not self.check_image(): 
            return
            
        try:
            value = float(self.division_entry.get())
            if not (1.0 <= value <= 10.0):
                messagebox.showerror("Error", "Please enter a value between 1.0 and 10.0")
                return
                
            self.division_var.set(value)
            self.processed_image = np.clip(self.original_image / value, 0, 255).astype(np.uint8)
            self.display_image(self.processed_image, self.processed_canvas)
            self.status_var.set(f"✅ Division by {value:.2f} applied")
            self.division_entry.config(bg=self.colors['input_bg'])
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number between 1.0 and 10.0")
        
    def add_info_section(self, parent):
        """Add image info section with larger text"""
        header = tk.Frame(parent, bg=self.colors['success'], height=40)
        header.pack(fill='x', padx=12, pady=(12, 0))
        header.pack_propagate(False)
        
        tk.Label(header, text="ℹ️ IMAGE INFO", font=('Segoe UI', 11, 'bold'),
                bg=self.colors['success'], fg='white').pack(pady=10)
        
        info_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        info_frame.pack(fill='x', padx=12, pady=(0, 15))
        
        self.info_label = tk.Label(info_frame, text="No image loaded",
                                  font=('Segoe UI', 10), justify='left',
                                  bg=self.colors['bg_card'], fg=self.colors['text_secondary'])
        self.info_label.pack(padx=15, pady=12, anchor='w')
        
    def create_button(self, parent, text, command, bg_color):
        """Create larger, more readable buttons with hover effects"""
        btn = tk.Button(parent, text=text, command=command,
                       font=('Segoe UI', 10, 'bold'),
                       bg=bg_color, fg='white', relief='flat',
                       cursor='hand2', padx=20, pady=10,
                       activebackground=self.colors['button_hover'],
                       activeforeground='white', bd=0)
        
        def on_enter(e): btn.config(bg=self.colors['button_hover'])
        def on_leave(e): btn.config(bg=bg_color)
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn
        
    def create_image_panel(self):
        """Create image display panel"""
        panel = tk.Frame(self.root, bg=self.colors['bg_primary'])
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(panel, style='Dark.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Original image tab
        original_frame = tk.Frame(self.notebook, bg=self.colors['bg_card'])
        self.notebook.add(original_frame, text="🖼️ ORIGINAL")
        
        self.original_canvas = tk.Canvas(original_frame, bg='#0a0a0a', highlightthickness=0)
        self.original_canvas.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Processed image tab
        processed_frame = tk.Frame(self.notebook, bg=self.colors['bg_card'])
        self.notebook.add(processed_frame, text="✨ PROCESSED")
        
        self.processed_canvas = tk.Canvas(processed_frame, bg='#0a0a0a', highlightthickness=0)
        self.processed_canvas.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Histogram tab
        histogram_frame = tk.Frame(self.notebook, bg=self.colors['bg_card'])
        self.notebook.add(histogram_frame, text="📊 HISTOGRAM")
        
        self.histogram_frame = histogram_frame
        
        # Add placeholders
        self.add_placeholder(self.original_canvas, "📁 Load an image to start")
        self.add_placeholder(self.processed_canvas, "🎨 Processed image will appear here")
        
        return panel
        
    def add_placeholder(self, canvas, text):
        """Add placeholder text with larger font"""
        canvas.create_text(400, 250, text=text, font=('Segoe UI', 13),
                          fill=self.colors['text_secondary'])
                          
    def create_status_bar(self):
        """Create status bar"""
        status_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=30)
        status_frame.pack(side='bottom', fill='x')
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="🟢 Ready - Load an image to begin")
        tk.Label(status_frame, textvariable=self.status_var,
                font=('Segoe UI', 9), bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary']).pack(side='left', padx=15, pady=6)
                
    def display_image(self, image, canvas):
        """Display image with auto-scaling"""
        if image is None:
            return
            
        canvas.delete("all")
        canvas.update_idletasks()
        
        canvas_width = max(canvas.winfo_width(), 300)
        canvas_height = max(canvas.winfo_height(), 200)
        
        h, w = image.shape[:2]
        scale = min((canvas_width-20)/w, (canvas_height-20)/h, 1.0)
        new_w, new_h = max(int(w*scale), 1), max(int(h*scale), 1)
        
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        if len(image.shape) == 3:
            pil_image = Image.fromarray(resized)
        else:
            pil_image = Image.fromarray(resized, mode='L')
            
        photo = ImageTk.PhotoImage(pil_image)
        
        x, y = canvas_width//2, canvas_height//2
        canvas.create_image(x, y, anchor="center", image=photo)
        canvas.image = photo
        
    # ==================== OPERATIONS ====================
    
    def load_image(self):
        """Load image file"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")])
            
        if file_path:
            try:
                self.original_image = cv2.imread(file_path)
                self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
                self.processed_image = self.original_image.copy()
                self.image_path = file_path
                
                self.display_image(self.original_image, self.original_canvas)
                self.display_image(self.processed_image, self.processed_canvas)
                
                # Update info
                h, w = self.original_image.shape[:2]
                filename = os.path.basename(file_path)
                size_kb = os.path.getsize(file_path) / 1024
                
                info = f"📄 {filename}\n📐 {w} × {h} pixels\n💾 {size_kb:.1f} KB"
                self.info_label.config(text=info)
                self.status_var.set(f"✅ Loaded: {filename}")
                
                self.notebook.select(1)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")
                
    def convert_grayscale(self):
        """Convert to grayscale"""
        if not self.check_image(): return
        self.processed_image = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
        self.display_image(self.processed_image, self.processed_canvas)
        self.status_var.set("✅ Converted to grayscale")
        
    def convert_binary(self):
        """Convert to binary"""
        if not self.check_image(): return
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY) if len(self.original_image.shape) == 3 else self.original_image
        _, self.processed_image = cv2.threshold(gray, self.threshold_var.get(), 255, cv2.THRESH_BINARY)
        self.display_image(self.processed_image, self.processed_canvas)
        self.status_var.set(f"✅ Binary conversion (threshold: {self.threshold_var.get()})")
        
    def logical_not(self):
        """Logical NOT operation (invert)"""
        if not self.check_image(): return
        self.processed_image = cv2.bitwise_not(self.original_image)
        self.display_image(self.processed_image, self.processed_canvas)
        self.status_var.set("✅ Logical NOT operation completed")
        
    def show_histogram(self):
        """Show histogram"""
        if not self.check_image(): return
        
        # Clear previous histogram
        for widget in self.histogram_frame.winfo_children():
            widget.destroy()
            
        try:
            # Use processed image for histogram if available
            img_for_hist = self.processed_image if self.processed_image is not None else self.original_image
            
            fig = Figure(figsize=(6, 4), facecolor='#0f3460')
            
            if len(img_for_hist.shape) == 3:
                ax = fig.add_subplot(111, facecolor='#1a1a2e')
                colors = ['red', 'green', 'blue']
                for i, color in enumerate(colors):
                    hist = cv2.calcHist([img_for_hist], [i], None, [256], [0, 256])
                    ax.plot(hist, color=color, alpha=0.7, linewidth=2)
                ax.set_title('RGB Histogram', color='white', fontsize=12, fontweight='bold')
            else:
                ax = fig.add_subplot(111, facecolor='#1a1a2e')
                hist = cv2.calcHist([img_for_hist], [0], None, [256], [0, 256])
                ax.plot(hist, color='cyan', linewidth=2)
                ax.set_title('Grayscale Histogram', color='white', fontsize=12, fontweight='bold')
            
            ax.set_xlabel('Pixel Intensity', color='white')
            ax.set_ylabel('Frequency', color='white')
            ax.tick_params(colors='white')
            ax.grid(True, alpha=0.3)
            
            canvas = FigureCanvasTkAgg(fig, self.histogram_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=8, pady=8)
            
            self.notebook.select(2)
            self.status_var.set("✅ Histogram displayed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show histogram:\n{str(e)}")
    
    def gaussian_blur(self):
        """Gaussian blur filter"""
        if not self.check_image(): return
        self.processed_image = cv2.GaussianBlur(self.original_image, (15, 15), 0)
        self.display_image(self.processed_image, self.processed_canvas)
        self.status_var.set("✅ Gaussian blur applied")
        
    def sharpen_image(self):
        """Sharpen filter"""
        if not self.check_image(): return
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        self.processed_image = cv2.filter2D(self.original_image, -1, kernel)
        self.display_image(self.processed_image, self.processed_canvas)
        self.status_var.set("✅ Image sharpened")
        
    def erosion_square(self):
        """Erosion with square structuring element"""
        if not self.check_image(): return
        
        if len(self.original_image.shape) == 3:
            gray = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        else:
            binary = self.original_image
            
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        self.processed_image = cv2.erode(binary, kernel, iterations=1)
        self.display_image(self.processed_image, self.processed_canvas)
        self.status_var.set("✅ Erosion with square SE applied")
        
    def erosion_cross(self):
        """Erosion with cross structuring element"""
        if not self.check_image(): return
        
        if len(self.original_image.shape) == 3:
            gray = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        else:
            binary = self.original_image
            
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
        self.processed_image = cv2.erode(binary, kernel, iterations=1)
        self.display_image(self.processed_image, self.processed_canvas)
        self.status_var.set("✅ Erosion with cross SE applied")
        
    def reset_image(self):
        """Reset to original image"""
        if not self.check_image(): return
        self.processed_image = self.original_image.copy()
        self.display_image(self.processed_image, self.processed_canvas)
        self.division_var.set(2.0)
        self.threshold_var.set(128)
        self.status_var.set("✅ Reset to original")
        
    def save_image(self):
        """Save processed image"""
        if self.processed_image is None:
            messagebox.showwarning("Warning", "No processed image to save!")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Processed Image",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
            
        if file_path:
            try:
                if len(self.processed_image.shape) == 3:
                    img_save = cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2BGR)
                else:
                    img_save = self.processed_image
                cv2.imwrite(file_path, img_save)
                self.status_var.set(f"✅ Saved: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", "Image saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save:\n{str(e)}")
                
    def check_image(self):
        """Check if image is loaded"""
        if self.original_image is None:
            messagebox.showwarning("Warning", "Please load an image first!")
            return False
        return True

def main():
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()