import tkinter as tk
from tkinter import ttk
import sys
import os
import json
from PIL import Image, ImageTk

# Add parent directory to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from AddClassGUI import AddClassApp
from DeleteUserGUI import DeleteUserGUI
from SignUpGUI import SignUpApp

# Import your database and other utilities here
import firebase_admin as fb
from firebase_admin import credentials, auth, db

# Get database URL from UserCredentials.json
firebase_credentials_user = json.load(open("Credentials/UserCredentials.json", "r"))
database_credential = {"databaseURL" : firebase_credentials_user["databaseURL"]}

# Initialize Firebase
try:
    cred = credentials.Certificate("Credentials/AdminCredentials.json")
    fb.initialize_app(cred, database_credential)
    database = db
    Auth = auth
except Exception as e:
    print(f"Failed to initialize Firebase: {str(e)}")
    exit()

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("User Management System")
        
        # Configure root window
        self.root.configure(bg='white')

        # Set window size and center it
        window_width = 600
        window_height = 400

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Get path to icon
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(self.script_dir, "..", "resources", "Icon.ico")
        image_path = os.path.abspath(image_path)

        self.main_image_path = os.path.join(self.script_dir, "..", "resources", "MainImage.png")
        self.main_image_path = os.path.abspath(self.main_image_path)

        try:
            self.root.iconbitmap(image_path)  # Set the icon for the window
        except tk.TclError:
            print(f"Could not load icon from {image_path}")

        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)

        self.root.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")

        # Create style templates
        self.create_styles()
        
        # Create main frame with blue and white styling
        self.main_frame = tk.Frame(self.root, bg='white')
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Create header frame
        self.create_header()
        
        # Create main menu
        self.create_main_menu()
        
        # Store reference to active frame or window
        self.active_frame = None
        self.active_window = None
        
        # Store references to module instances
        self.signup_app = None
        self.delete_user_gui = None
        self.add_class_app = None
        
        # Initialize database reference (you may need to adjust this)
        try:
            # Get database reference from your Firebase initialization
            self.database = database
        except ImportError:
            # If the module import fails, set to None for now
            self.database = None
    
    def create_styles(self):
        """Create and configure ttk styles for consistent UI"""
        style = ttk.Style()
        
        # Configure the style to have a blue background
        style.theme_use('clam')  # Using 'clam' theme for better custom styling
        
        # Create a custom button style with full blue background
        style.configure('Blue.TButton', 
                        background='#3498DB',   # Blue background
                        foreground='white',     # White text
                        font=('Arial', 10, 'bold'),
                        padding=10)
        
        # Map additional states for hover and active states
        style.map('Blue.TButton',
                  background=[('active', '#2980B9'), 
                              ('pressed', '#21618C')],
                  foreground=[('active', 'white'), 
                              ('pressed', 'white')])
        
        # Configure the OptionMenu style
        style.configure('Custom.TMenubutton', 
                background='white', 
                foreground='#2C3E50',  # Dark text color
                font=('Arial', 10),
                borderwidth=1,
                relief='solid')
        
        # Header style
        style.configure('Header.TLabel',
                        font=('Arial', 22, 'bold'),
                        foreground='#2C3E50',
                        background='white')
                        
        # Description style
        style.configure('Description.TLabel',
                        font=('Arial', 12),
                        foreground='#7F8C8D',
                        background='white')
                        
    def create_header(self):
        """Create the application header with image"""
        header_frame = tk.Frame(self.main_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Create a horizontal layout frame for image and title
        title_row = tk.Frame(header_frame, bg='white')
        title_row.pack(fill='x')
        
        # Load and resize the main image
        try:
            # Load image with PIL
            original_image = Image.open(self.main_image_path)
            
            # Calculate appropriate size (height of about 70-80 pixels, maintaining aspect ratio)
            img_height = 80
            aspect_ratio = original_image.width / original_image.height
            img_width = int(img_height * aspect_ratio)
            
            # Resize image
            resized_image = original_image.resize((img_width, img_height), Image.LANCZOS)
            
            # Convert to PhotoImage
            self.main_photo = ImageTk.PhotoImage(resized_image)
            
            # Create and place image label
            image_label = tk.Label(title_row, image=self.main_photo, bg='white')
            image_label.pack(side='left', padx=(0, 15))
            
        except Exception as e:
            print(f"Error loading main image: {e}")
        
        # Title and description in a vertical frame
        text_frame = tk.Frame(title_row, bg='white')
        text_frame.pack(side='left', fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(text_frame, 
                              text="User Management System", 
                              style='Header.TLabel')
        title_label.pack(anchor='w', pady=(5, 5))
        
        # Description
        desc_label = ttk.Label(text_frame, 
                             text="Select an option to manage users and classes", 
                             style='Description.TLabel')
        desc_label.pack(anchor='w')
        
        # Separator
        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.pack(fill='x', pady=(10, 20))
    
    def create_main_menu(self):
        """Create the main menu buttons"""
        self.menu_frame = tk.Frame(self.main_frame, bg='white')
        self.menu_frame.pack(expand=True, fill='both')
        
        # Create three buttons with descriptions
        self.create_option_button(
            "User Sign Up", 
            "Register a new user account",
            self.open_signup
        )
        
        self.create_option_button(
            "Add Class", 
            "Create and configure a new class",
            self.open_add_class
        )

        self.create_option_button(
            "Delete User", 
            "Remove an existing user account",
            self.open_delete_user
        )
        
    
    def create_option_button(self, title, description, command):
        """Create a styled option button with title and description"""
        option_frame = tk.Frame(self.menu_frame, bg='white', pady=10)
        option_frame.pack(fill='x', pady=5)
        
        # Button
        button = ttk.Button(
            option_frame, 
            text=title, 
            command=command,
            style='Blue.TButton',
            width=15
        )
        button.pack(side='left', padx=(0, 15))
        
        # Description text
        desc_label = tk.Label(
            option_frame,
            text=description,
            font=("Arial", 11),
            fg='#2C3E50',
            bg='white',
            anchor='w'
        )
        desc_label.pack(side='left', fill='x')
    
    def clear_main_frame(self):
        """Clear the main frame to prepare for new content"""
        # Hide the menu frame
        self.menu_frame.pack_forget()
        
        # Remove any active frames
        if self.active_frame:
            self.active_frame.pack_forget()
            self.active_frame = None
    
    def show_main_menu(self):
        """Return to main menu"""
        # Clear any active content
        if self.active_frame:
            self.active_frame.pack_forget()
            self.active_frame = None
        
        # Show the menu frame
        self.menu_frame.pack(expand=True, fill='both')
    
    def open_signup(self):
        """Open the Sign Up interface"""
        self.clear_main_frame()
        
        # Create a new toplevel window for signup
        signup_window = tk.Toplevel(self.root)
        signup_window.title("Sign Up")
        
        # Set window size and center it
        window_width = 600
        window_height = 400
        screen_width = signup_window.winfo_screenwidth()
        screen_height = signup_window.winfo_screenheight()
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)
        signup_window.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")
        
        # Configure icon
        try:
            signup_window.iconbitmap(os.path.join(self.script_dir, "..", "resources", "Icon.ico"))
        except tk.TclError:
            pass
        
        # Configure styling
        signup_window.configure(bg="white")
        
        # Create a modified SignUpApp instance
        self.signup_app = SignUpApp(signup_window, database=database, Auth=Auth)
        
        # Configure what happens when window is closed
        def on_close():
            signup_window.destroy()
            self.root.deiconify()  # Show main window again
            self.show_main_menu()
        
        signup_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # Add a back button
        back_frame = tk.Frame(signup_window, bg='white')
        back_frame.pack(side='bottom', fill='x', padx=20, pady=10)
        
        
        # Hide the main window while signup is open
        self.root.withdraw()
        
    def open_delete_user(self):
        """Open the Delete User interface"""
        self.clear_main_frame()
        
        # Create a new toplevel window for delete user
        delete_window = tk.Toplevel(self.root)
        delete_window.title("Delete User")
        
        # Set window size and center it
        window_width = 400
        window_height = 300
        screen_width = delete_window.winfo_screenwidth()
        screen_height = delete_window.winfo_screenheight()
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)
        delete_window.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")
        
        # Configure icon
        try:
            delete_window.iconbitmap(os.path.join(self.script_dir, "..", "resources", "Icon.ico"))
        except tk.TclError:
            pass
        
        # Configure styling
        delete_window.configure(bg="white")
        
        # Create a modified DeleteUserGUI instance
        self.delete_user_gui = DeleteUserGUI(delete_window, database=database, auth=Auth)
        
        # Configure what happens when window is closed
        def on_close():
            delete_window.destroy()
            self.root.deiconify()  # Show main window again
            self.show_main_menu()
        
        delete_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # Add a back button
        back_frame = tk.Frame(delete_window, bg='white')
        back_frame.pack(side='bottom', fill='x', padx=20, pady=10)
        
        
        # Hide the main window while delete user is open
        self.root.withdraw()
    
    def open_add_class(self):
        """Open the Add Class interface"""
        self.clear_main_frame()
        
        # Create a new toplevel window for add class
        add_class_window = tk.Toplevel(self.root)
        add_class_window.title("Add Class")
        
        # Set window size and center it
        window_width = 400
        window_height = 300
        screen_width = add_class_window.winfo_screenwidth()
        screen_height = add_class_window.winfo_screenheight()
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)
        add_class_window.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")
        
        # Configure icon
        try:
            add_class_window.iconbitmap(os.path.join(self.script_dir, "..", "resources", "Icon.ico"))
        except tk.TclError:
            pass
        
        # Configure styling
        add_class_window.configure(bg="white")
        
        # Pass the database reference if available
        self.add_class_app = AddClassApp(add_class_window, database=database)
        
        # Configure what happens when window is closed
        def on_close():
            add_class_window.destroy()
            self.root.deiconify()  # Show main window again
            self.show_main_menu()
        
        add_class_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # Add a back button
        back_frame = tk.Frame(add_class_window, bg='white')
        back_frame.pack(side='bottom', fill='x', padx=20, pady=10)
        
        
        # Hide the main window while add class is open
        self.root.withdraw()


# Main entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()