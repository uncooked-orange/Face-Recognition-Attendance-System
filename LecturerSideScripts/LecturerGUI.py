import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import jwt
from datetime import datetime
from PIL import Image, ImageTk
import json
import os
import cv2
import threading
import pyrebase as pb
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from GeneralUtilities.UtilityChecks import check_email_valid, check_password_valid
from LecturerUtilities.StudentJSON import AttendanceManager
from GeneralUtilities.Detection import FaceRecognitionSystem

firebaseConfig = json.load(open("Credentials/UserCredentials.json","r"))
class SignInApp:
    def __init__(self, root):
        # Initialize Window
        self.root = root
        self.root.title("Attendance Management System")
        
        # Set window size and center it
        window_width = 600
        window_height = 350
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = (screen_width / 2) - (window_width / 2)
        self.y = (screen_height / 2) - (window_height / 2)
        self.root.geometry("%dx%d+%d+%d" % (window_width, window_height, self.x, self.y))
        self.root.resizable(False, False)
        
        # Initializing frames
        self.intro_frame = tk.Frame(self.root, bg="white")
        self.mode_selection_frame = tk.Frame(self.root, bg="white")
        self.sign_in_frame = tk.Frame(self.root, bg="white")
        self.classes_frame = tk.Frame(self.root, bg="white")
        self.study_frame = tk.Frame(self.root, bg="white")
        self.attendance_taking_method_frame = tk.Frame(self.root, bg="white")
        self.select_week_frame = tk.Frame(self.root, bg="white")
        self.camera_frame = tk.Frame(self.root, bg="white")
        self.detection_frame = tk.Frame(self.root, bg="white")
        self.attendance_frame = tk.Frame(self.root, bg="white")
        self.branch_frame = tk.Frame(self.root, bg="white")
        
        self.script_dir = os.path.dirname(os.path.abspath(__file__))  # path to script
        icon_path = os.path.join(self.script_dir, "..", "resources", "Icon.ico")
        icon_path = os.path.abspath(icon_path)
        
        self.root.iconbitmap(icon_path)  # Set the icon for the window
        
        # Style the root
        self.root.configure(bg="white")
        
        # Create style templates
        style = ttk.Style()
        
        # Configure the style to have a blue background
        style.theme_use('clam')  # Using 'clam' theme for better custom styling
        
        # Create a custom button style with full blue background
        style.configure('Blue.TButton',
                        background='#3498DB',   # Blue background
                        foreground='white',     # White text
                        font=('Arial', 10, 'bold'))
        
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
        
        # Initialize attendance manager and local data
        self.attendance_manager = None
        
        # Setup intro frame
        self.setup_intro_frame()
        
        # Display the intro frame initially
        self.show_intro_frame()
    
    def setup_intro_frame(self):
        """Setup the introduction frame with main image and start button"""
        # clear all frames
        self.clear_frames()
        # Create and configure the intro frame to fill the window
        self.intro_frame.pack(fill=tk.BOTH, expand=True)
        self.intro_frame.pack_propagate(False)
        self.intro_frame.configure(width=650, height=300)
        
        # Load the main image
        main_image_path = os.path.join(self.script_dir, "..", "resources", "MainImage.png")
        main_image_path = os.path.abspath(main_image_path)
        
        try:
            # Use PIL to open the image
            image = Image.open(main_image_path)
            
            # Resize if needed to fit the frame while maintaining aspect ratio
            max_width, max_height = 400, 150
            img_width, img_height = image.size
            
            # Calculate new dimensions to maintain aspect ratio
            if img_width > max_width or img_height > max_height:
                ratio = min(max_width/img_width, max_height/img_height)
                img_width = int(img_width * ratio)
                img_height = int(img_height * ratio)
                image = image.resize((img_width, img_height), Image.LANCZOS)
            
            # Convert to PhotoImage for Tkinter
            self.main_image = ImageTk.PhotoImage(image)
            
            # Create a label to display the image
            image_label = tk.Label(self.intro_frame, image=self.main_image, bg="white")
            image_label.pack(pady=(20, 10))
            
        except Exception as e:
            # If image loading fails, show an error message instead
            error_label = tk.Label(self.intro_frame, 
                                    text="Unable to load image.\nPlease ensure 'MainImage.png' is in the resources folder.",
                                    bg="white", fg="red", font=("Arial", 12))
            error_label.pack(pady=(50, 10))
            print(f"Error loading image: {e}")
        
        # Welcome text
        welcome_label = tk.Label(self.intro_frame, 
                                 text="Welcome to Attendance Management System",
                                 bg="white", fg="#2C3E50", font=("Arial", 14, "bold"))
        welcome_label.pack(pady=(5, 15))
        
        # Start button
        start_button = ttk.Button(self.intro_frame, text="Get Started", 
                                  style='Blue.TButton', 
                                  command=self.show_mode_selection_frame)
        start_button.pack(pady=(0, 20))
    
    def show_intro_frame(self):
        """Show the introduction frame and hide all others"""
        # Hide all frames
        for frame in (self.mode_selection_frame, self.sign_in_frame, self.classes_frame, 
                     self.study_frame, self.attendance_taking_method_frame, 
                     self.select_week_frame, self.camera_frame, self.detection_frame, 
                     self.attendance_frame, self.branch_frame):
            frame.pack_forget()
        
        # Show intro frame
        self.intro_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_mode_selection_frame(self):
        """Displays the mode selection frame with Online and Offline options."""
        # Clear all frames
        self.clear_frames()

        # Initialize mode variable
        self.mode = ""

        # Title
        tk.Label(self.mode_selection_frame,background="white", text="Select Operation Mode", font=("Arial", 16)).pack(pady=20)

        # Online Mode Button
        online_btn = ttk.Button(self.mode_selection_frame,style="Blue.TButton", text="Online Mode", 
                                command=self.setup_online_mode, 
                                width=20)
        online_btn.pack(pady=10)

        # Offline Mode Button
        offline_btn = ttk.Button(self.mode_selection_frame,style="Blue.TButton", text="Offline Mode", 
                                 command=self.setup_offline_mode, 
                                 width=20)
        offline_btn.pack(pady=10)

        self.mode_selection_frame.pack(expand=True)

    def setup_online_mode(self):
        """Prepare for online mode by allowing user to choose between existing JSON or creating a new one."""
        self.mode = "online"

        try:
            # Create a popup to choose between existing file and new file
            self.online_mode_choice = messagebox.askyesno(
                "File Selection", 
                "Do you want to use an existing students JSON file?\n\n"
                "Yes: Select an existing file\n"
                "No: Create a new file location"
            )

            if self.online_mode_choice:
                # Option 1: Select existing JSON file
                json_file_path = filedialog.askopenfilename(
                    title="Select Existing Students JSON File",
                    filetypes=[("JSON files", "*.json")]
                )

                if not json_file_path:
                    # User cancelled file selection
                    self.show_mode_selection_frame()
                    return

                # Set the JSON save path to the directory of the selected file
                self.json_save_path = os.path.dirname(json_file_path)
            else:
                # Option 2: Choose a new directory to save JSON file
                self.json_save_path = filedialog.askdirectory(
                    title="Select Directory to Save New Student Data"
                )

                if not self.json_save_path:
                    # User cancelled directory selection
                    self.show_mode_selection_frame()
                    return

            # Initialize Firebase for online mode
            firebase = pb.initialize_app(firebaseConfig)
            self.auth = firebase.auth()
            self.database = firebase.database()

            # Show sign-in frame
            self.show_sign_in_frame()

        except Exception as e:
            messagebox.showerror("Initialization Error", str(e))
            self.show_mode_selection_frame()

    def setup_offline_mode(self):
        """Prepare for offline mode by selecting JSON file."""

        self.mode = "offline"
        try:
            # Open file dialog to select JSON file
            json_file_path = filedialog.askopenfilename(
                title="Select Students JSON File",
                filetypes=[("JSON files", "*.json")]
            )
            
            if not json_file_path:
                # User cancelled file selection
                return
            
            # Create AttendanceManager in offline mode
            self.attendance_manager = AttendanceManager(
                database=None,  # No database in offline mode
                lecturer_id=None,  # Will be loaded from JSON
                local_data_path=os.path.dirname(json_file_path)
            )
            
            # Load local students from the selected JSON file
            self.local_data = self.attendance_manager.load_local_students(
                filename=os.path.basename(json_file_path)
            )
            
            # Save the JSON save path for offline mode
            self.json_save_path = os.path.dirname(json_file_path)

            if not self.local_data:
                messagebox.showerror("Error", "Invalid or empty JSON file")
                return
            
            # Set lecturer information from loaded data
            self.lecturer_name_variable = self.local_data['lecturer_info']['name']
            self.lecturer_classes_variable = self.local_data['lecturer_info']['classes']
            self.lecturer_id = self.local_data['lecturer_info']['id']
            
            # Proceed to classes frame with offline data
            self.show_classes_frame(offline_mode=True)
        
        except Exception as e:
            messagebox.showerror("Offline Mode Error", str(e))

    # Display Sign In Frame
    def show_sign_in_frame(self):
        """Sets up the sign_in frame with Email and Password entry fields and a Submit button."""
        # Clear all frames
        self.clear_frames()

        # Reset email and password variables
        self.email_variable = ""
        self.password_variable = ""

        # Setting up the email label and entry
        tk.Label(self.sign_in_frame,background="white", text="Email:").pack()
        self.email_entry = tk.Entry(self.sign_in_frame, width=30)
        self.email_entry.pack(pady=10)

        # Setting up the password label and entry
        tk.Label(self.sign_in_frame,background="white", text="Password:").pack()
        self.password_entry = tk.Entry(self.sign_in_frame, show="*", width=30)
        self.password_entry.pack(pady=10)

        # Submit button
        submit_btn = ttk.Button(self.sign_in_frame, text="Submit",style="Blue.TButton", command=self.on_submit_email_password)
        submit_btn.pack(pady=10)

        self.sign_in_frame.pack()

    # Display Classes Frame
    def show_classes_frame(self, offline_mode=False):
        """Displays the classes frame for the lecturer."""
        # Clear all frames
        self.clear_frames()

        # Reset chosen variables
        self.chosen_class_variable = ""
        self.study_type = ""
        self.branch_type = ""

        # Welcome message
        tk.Label(self.classes_frame,background="white",
                 text=f"Welcome, {self.lecturer_name_variable}\nChoose a Class:", 
                 font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=10)

        # Determine button width
        button_width = max(len(class_name) for class_name in self.lecturer_classes_variable) + 5
        
        # Create class buttons
        row = 1
        for class_name in self.lecturer_classes_variable:
            class_btn = ttk.Button(
                self.classes_frame, 
                style="Blue.TButton",
                text=class_name, 
                width=button_width, 
                command=lambda name=class_name: self.on_submit_chosen_class(name)
            )
            class_btn.grid(row=row, column=0, columnspan=2, pady=5)
            row += 1

        # Back button (goes to mode selection in offline mode)
        back_btn = ttk.Button(
            self.classes_frame,
            style="Blue.TButton", 
            text="Back", 
            command=self.show_mode_selection_frame
        )
        back_btn.grid(row=row + 1, column=0, columnspan=2, pady=10)

        self.classes_frame.pack()

    # Display Branch Frame
    def show_branch_frame(self):
        """
        Displays the branch frame with a selection of available branches for the chosen class and study type.
    
        This method:
        1. Clears existing frames
        2. Provides radio buttons for branch selection between IT and NE
        3. Offers navigation buttons to go back or submit the selection
    
        The branches are now predefined as IT and NE, regardless of local student data.
        """
        # Clear all frames
        self.clear_frames()
    
        # Reset branch type
        self.branch_type = ""
        self.study_type = ""
    
        # Title label
        tk.Label(self.branch_frame,background="white", text="Select Branch:", font=("Arial", 12)).grid(row=0, column=0, columnspan=2, pady=10)
    
        # Predefined branches
        available_branches = ["IT", "NE"]
    
        # Radio buttons for branches
        self.branch_variable = tk.StringVar(value=available_branches[0])
        for i, branch in enumerate(available_branches):
            branch_btn = tk.Radiobutton(
                self.branch_frame, 
                background="white",
                text=branch, 
                variable=self.branch_variable, 
                value=branch
            )
            branch_btn.grid(row=1, column=i, padx=10)
    
        # Back and Submit buttons
        back_btn = ttk.Button(
            self.branch_frame,
            style="Blue.TButton", 
            text="Back", 
            command=self.show_study_frame
        )
        back_btn.grid(row=2, column=0, pady=10)
        
        submit_btn = ttk.Button(
            self.branch_frame, 
            style="Blue.TButton",
            text="Submit", 
            command=self.on_submit_branch
        )
        submit_btn.grid(row=2, column=1, pady=10)
    
        self.branch_frame.pack()

        # Radio buttons for branches
        self.branch_variable = tk.StringVar(value=available_branches[0])
        for i, branch in enumerate(available_branches):
            branch_btn = tk.Radiobutton(
                self.branch_frame, 
                background="white",
                text=branch, 
                variable=self.branch_variable, 
                value=branch
            )
            branch_btn.grid(row=1, column=i, padx=10)

        # Back and Submit buttons
        back_btn = ttk.Button(
            self.branch_frame, 
            style="Blue.TButton",
            text="Back", 
            command=self.show_study_frame
        )
        back_btn.grid(row=2, column=0, pady=10)

        submit_btn = ttk.Button(
            self.branch_frame,
            style="Blue.TButton", 
            text="Submit", 
            command=self.on_submit_branch
        )
        submit_btn.grid(row=2, column=1, pady=10)

        self.branch_frame.pack()

    # Display Study Frame
    def show_study_frame(self):
        """Displays the study frame with two buttons for Morning and Evening."""
        # Clear all frames
        self.clear_frames()

        # Reset chosen variables
        self.study_type = ""

        tk.Label(self.study_frame,background="white", text="Select Type of Study:", font=("Arial", 12)).grid(row=0, column=0, columnspan=2, pady=10)

        # Radio buttons for Morning and Evening
        self.study_variable = tk.StringVar(value="Morning")
        study_options = ["Morning", "Evening"]
        for i, option in enumerate(study_options):
            study_btn = tk.Radiobutton(self.study_frame,background="white", text=option, variable=self.study_variable, value=option)
            study_btn.grid(row=1, column=i, padx=10)

        # Back and Submit buttons
        back_btn = ttk.Button(self.study_frame,style="Blue.TButton" ,text="Back", command=self.show_classes_frame)
        back_btn.grid(row=2, column=0, pady=10)
        submit_btn = ttk.Button(self.study_frame,style="Blue.TButton", text="Submit", command=self.on_submit_study)
        submit_btn.grid(row=2, column=1, pady=10)

        self.study_frame.pack()

    # Display Attendance Taking Method Frame
    def show_attendance_taking_method_frame(self):
        """Displays the attendance taking method frame with options for manual or automatic attendance."""
        # Clear all frames
        self.clear_frames()

        # Title label
        tk.Label(self.attendance_frame,background="white", text="Select Attendance Taking Method:", font=("Arial", 12)).grid(row=0, column=0, columnspan=2, pady=10)

        # Attendance taking methods
        attendance_methods = ["Manual", "Automatic"]

        # Radio buttons for attendance methods
        self.attendance_method_variable = tk.StringVar(value=attendance_methods[0])
        for i, method in enumerate(attendance_methods):
            method_btn = tk.Radiobutton(
                self.attendance_frame, 
                background="white",
                text=method, 
                variable=self.attendance_method_variable, 
                value=method
            )
            method_btn.grid(row=1, column=i, padx=10)

        # Back and Submit buttons
        back_btn = ttk.Button(
            self.attendance_frame, 
            style="Blue.TButton",
            text="Back", 
            command=self.show_branch_frame
        )
        back_btn.grid(row=2, column=0, pady=10)
        
        submit_btn = ttk.Button(
            self.attendance_frame,
            style="Blue.TButton", 
            text="Submit", 
            command=self.on_submit_attendance_method
        )
        submit_btn.grid(row=2, column=1, pady=10)

        self.attendance_frame.pack()

    # Select Week for attendance (Automatic Mode)
    def show_select_week_frame(self):
        """Displays the select week frame for automatic attendance mode."""
        # Clear all frames
        self.clear_frames()

        # Title label
        tk.Label(self.attendance_frame,background="white", text="Select Week for Attendance:", font=("Arial", 12)).grid(row=0, column=0, columnspan=2, pady=10)

        # Week selection drop down
        self.week_variable = tk.StringVar(value="1")
        week_options = [f"{i}" for i in range(1, 14)]  # Assuming 13 weeks
        week_dropdown = ttk.OptionMenu(self.attendance_frame, self.week_variable, *week_options,style="Custom.TMenubutton")
        week_dropdown.grid(row=1, column=0, columnspan=2, pady=10)

        # Back and Submit buttons
        back_btn = ttk.Button(self.attendance_frame,style="Blue.TButton", text="Back", command=self.show_attendance_taking_method_frame)
        back_btn.grid(row=2, column=0, pady=10)

        submit_btn = ttk.Button(self.attendance_frame, text="Submit",style="Blue.TButton", command=self.on_submit_week)
        submit_btn.grid(row=2, column=1, pady=10)

        self.attendance_frame.pack()

    # Select Camera to record with (Automatic Mode)
    def show_camera_frame(self):
        """Displays frame for camera selection with available options."""
        self.clear_frames()

        # Reset camera variable
        self.camera_index = None

        tk.Label(self.camera_frame,background="white", text="Select Camera:", font=("Arial", 12)).grid(row=0, column=0, columnspan=2, pady=10)

        # Get available cameras
        cameras = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    cameras.append(f"Camera {i}")
                cap.release()

        if not cameras:
            messagebox.showerror("Error", "No cameras found")
            self.show_select_week_frame()
            return

        # Camera selection radio buttons
        self.camera_variable = tk.StringVar(value=cameras[0])
        for i, camera in enumerate(cameras):
            camera_btn = tk.Radiobutton(
                self.camera_frame, 
                background="white",
                text=camera, 
                variable=self.camera_variable, 
                value=camera
            )
            camera_btn.grid(row=1, column=i, padx=10)

        # Back and Submit buttons
        back_btn = ttk.Button(
            self.camera_frame,
            style="Blue.TButton", 
            text="Back", 
            command=self.show_select_week_frame
        )
        back_btn.grid(row=2, column=0, pady=10)

        submit_btn = ttk.Button(
            self.camera_frame, 
            style="Blue.TButton",
            text="Submit", 
            command=self.on_submit_camera
        )
        submit_btn.grid(row=2, column=1, pady=10)

        self.camera_frame.pack()

    def show_detection_frame(self):
        """Shows frame with student detection log while camera feeds runs in separate window."""
        self.clear_frames()
    
        # Initialize face recognition system
        self.face_system = FaceRecognitionSystem()
        self.face_system.load_students_from_json(
            f"{self.json_save_path}/students.json",
            self.chosen_class_variable
        )
    
        # Initialize detected students set
        self.detected_students = set()
    
        # Create main container frame
        container = tk.Frame(self.attendance_frame,background="white")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
        # Title with class and week information
        title_text = f"Attendance Log - {self.chosen_class_variable} (Week {self.week})"
        title_label = tk.Label(
            container, 
            background="white",
            text=title_text,
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
    
        # Create log frame with scrollbar
        log_frame = tk.Frame(container,background="white")
        log_frame.pack(fill=tk.BOTH, expand=True)
    
        # Add scrollbar
        scrollbar = tk.Scrollbar(log_frame,background="white")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        # Create log display with increased size and better visibility
        self.log_text = tk.Text(
            log_frame,
            background="white",
            height=10,
            width=60,
            font=("Arial", 12),
            yscrollcommand=scrollbar.set,
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
    
        # Control buttons frame
        button_frame = tk.Frame(container,background="white")
        button_frame.pack(fill=tk.X, pady=10)
    
        # Control buttons
        stop_btn = ttk.Button(
            button_frame,
            style="Blue.TButton",
            text="Stop and Save",
            command=self.stop_detection,
            width=15
        )
        stop_btn.pack(side=tk.LEFT, padx=5)
    
        back_btn = ttk.Button(
            button_frame,
            style="Blue.TButton",
            text="Cancel",
            command=self.cancel_detection,
            width=15
        )
        back_btn.pack(side=tk.LEFT, padx=5)
    
        self.attendance_frame.pack(fill=tk.BOTH, expand=True)
    
        # Start camera feed and detection in separate thread
        self.detection_active = True
        self.camera_thread = threading.Thread(target=self.run_detection)
        self.camera_thread.start()

    def run_detection(self):
        """Run face detection and recognition with bounding boxes."""
        # Initialize camera
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            messagebox.showerror("Error", "Failed to open camera. Please check camera connection.")
            return
    
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
        # Initialize variables
        face_system = self.face_system
        self.detected_students = set()
        last_detection_time = time.time()
        detection_interval = 5.0  # Detection performed every 5 seconds
        
        # Main processing loop
        while self.detection_active:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            display_frame = frame.copy()  # Create a copy for display purposes
            current_time = time.time()
            
            # Detect faces in every frame for drawing bounding boxes
            faces = face_system.detect_faces(frame)
            
            # Draw bounding boxes for all detected faces
            if faces is not None:
                for face in faces:
                    # Extract face coordinates
                    x, y, w, h = face[:4]  # First 4 elements should be bounding box coordinates
                    
                    # Draw rectangle around face
                    cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Perform recognition only every 5 seconds
            if current_time - last_detection_time >= detection_interval:
                # Process frame for recognition
                _, recognized_ids = face_system.process_frame(frame)
                last_detection_time = current_time
                
                # Update UI with newly detected students
                self.process_recognized_students(recognized_ids)
                    
            # Display frame with bounding boxes
            cv2.imshow('Camera Feed', display_frame)
            
            # Check for quit command
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
    
    def process_recognized_students(self, recognized_ids):
        """Process recognized student IDs and update UI."""
        for student_id in recognized_ids:
            # Check if this is a new detection and student exists in our database
            if (student_id not in self.detected_students and 
                student_id in self.local_data['students'][self.study_type][self.branch_type]):
                
                # Add to detected set
                self.detected_students.add(student_id)
                
                # Get student name
                student_name = self.local_data['students'][self.study_type][self.branch_type][student_id]['name']
                
                # Format and log detection
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_msg = f"[{timestamp}] {student_name}\n"
                
                # Update UI in thread-safe way
                self.log_text.after(0, self.update_log, log_msg)  

    def update_log(self, message):
        """Updates the log text safely from any thread."""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)  # Auto-scroll to bottom  

    def stop_detection(self):
        """Stops the detection process and saves attendance."""
        self.detection_active = False
        if hasattr(self, 'camera_thread'):
            self.camera_thread.join()
            self.submit_detected_students() 

    def cancel_detection(self):
        """Cancels the detection process without saving."""
        self.detection_active = False
        if hasattr(self, 'camera_thread'):
            self.camera_thread.join()
        self.show_attendance_taking_method_frame()  

    def submit_detected_students(self):
        """Submits the detected students and updates the attendance data."""
        try:
            if not hasattr(self, 'detected_students') or not self.detected_students:
                messagebox.showwarning("No Attendance", "No students were detected.")
                self.show_attendance_taking_method_frame()
                return  

            students_updated = 0
            # Iterate through detected students and update attendance
            for student_id in self.detected_students:
                try:
                    # Get student data
                    student_data = self.local_data['students'][self.study_type][self.branch_type].get(student_id)
                    if not student_data:
                        print(f"Warning: Student {student_id} not found in local data")
                        continue    

                    # Update attendance for the specific class
                    if self.chosen_class_variable in student_data['classes']:
                        student_data['classes'][self.chosen_class_variable][self.week-1] = 1
                        students_updated += 1
                    else:
                        print(f"Warning: Class {self.chosen_class_variable} not found for student {student_id}")    

                except KeyError as e:
                    print(f"Error updating student {student_id}: {e}")
                    continue    

            if students_updated > 0:
                # Save to local file
                self.attendance_manager.local_students = self.local_data
                self.attendance_manager.save_students_locally() 

                # Handle online/offline modes
                if self.mode == "online":
                    try:
                        self.attendance_manager.upload_local_students()
                        messagebox.showinfo("Success", 
                                          f"Attendance successfully updated for {students_updated} students and uploaded")
                    except Exception as e:
                        messagebox.showwarning("Partial Success", 
                                             f"Attendance saved locally for {students_updated} students but failed to upload: {str(e)}")
                else:
                    messagebox.showinfo("Success", 
                                      f"Attendance successfully updated for {students_updated} students")
            else:
                messagebox.showwarning("No Updates", "No student records were updated.")    

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update attendance: {str(e)}")
        finally:
            self.show_attendance_taking_method_frame()

    def on_submit_camera(self):
        """Handles camera selection and starts detection."""
        camera_str = self.camera_variable.get()
        self.camera_index = int(camera_str.split()[-1])
        self.show_detection_frame()

    def show_attendance_frame(self):
        """
        Displays the attendance frame as a paginated table with student names as rows and weeks as columns with checkboxes.

        This method:
        1. Clears existing frames
        2. Filters students based on selected class, study type, and branch
        3. Sets up pagination for the student list
        4. Prepares the display of students

        The method uses locally stored student data with additional branch-level filtering.
        """
        self.clear_frames()

        self.students_per_page = 8
        self.current_page = 0
        self.student_attendances = {}

        try:
            if not hasattr(self, 'local_data') or not self.local_data:
                raise Exception("No local student data available. Please fetch students first.")

            # Access students from restructured data
            all_students = self.local_data['students'].get(self.study_type, {}).get(self.branch_type, {})

            if not all_students:
                raise Exception(f"No students found for {self.study_type}, branch {self.branch_type}")

            # Filter and format student data
            students_list = {}
            for student_id, student_info in all_students.items():
                if self.chosen_class_variable in student_info['classes']:
                    students_list[student_id] = {
                        student_info['name']: student_info['classes'][self.chosen_class_variable]
                    }

            if not students_list:
                raise Exception(f"No students found in class {self.chosen_class_variable}")

            # Sort students by name
            students_list = dict(sorted(students_list.items(), key=lambda x: list(x[1].keys())[0]))

            self.all_students = list(students_list.items())
            self.total_pages = (len(self.all_students) - 1) // self.students_per_page + 1

            self.display_students_page()

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.show_study_frame()

    # Display Students Page
    def display_students_page(self):
        """Displays the students on the current page with attendance checkboxes for each week."""
        # Clear all frames
        self.clear_frames()

        # Define name column width in characters (reduced for more space)
        name_max_width = 20  # Reduced from 20 to 15
        name_column_width = 50  # Reduced pixel width

        # Configure the attendance frame to use a more efficient grid
        self.attendance_frame.grid_columnconfigure(0, minsize=name_column_width)  # Fixed width for name column
        for week in range(1, 14):
            self.attendance_frame.grid_columnconfigure(week, minsize=35)  # Smaller fixed width for week columns

        # Week header (Weeks 1-13 as columns)
        name_header = tk.Label(self.attendance_frame, background="white", text="Name", 
                             font=("Arial", 9, "bold"))  # Smaller font
        name_header.grid(row=1, column=0, padx=2, pady=3, sticky="w")  # Reduced padding

        for week in range(1, 14):  # Assuming 13 weeks
            tk.Label(self.attendance_frame, background="white", text=f"{week}", 
                   font=("Arial", 9, "bold")).grid(row=1, column=week, padx=2, pady=3)  # Reduced padding

        # Determine which students to display for the current page
        start_index = self.current_page * self.students_per_page
        end_index = start_index + self.students_per_page
        current_students = self.all_students[start_index:end_index]

        row_index = 2
        for student_id, student_info in current_students:
            student_name = list(student_info.keys())[0]

            # Format name to fit within constraints (single line with ellipsis)
            formatted_name = self.truncate_name(student_name, name_max_width)

            # Create a label with fixed width
            name_label = tk.Label(self.attendance_frame, background="white", text=formatted_name,
                                font=("Arial", 9), anchor="w")  # Smaller font
            name_label.grid(row=row_index, column=0, padx=2, pady=2, sticky="w")  # Reduced padding

            # Initialize attendance dictionary for the student
            self.student_attendances[student_id] = {}

            # Create checkboxes for each week (present/absent for each week)
            for week in range(1, 14):
                week_var = tk.BooleanVar()  # Track presence for each week

                # Use a more compact checkbox
                checkbox = tk.Checkbutton(self.attendance_frame, background="white", 
                                        variable=week_var, onvalue=True, offvalue=False,
                                        padx=0, pady=0)  # Minimal internal padding

                # Check the checkbox if the student was present in this week
                checkbox.select() if student_info[student_name][week-1] else checkbox.deselect()
                checkbox.grid(row=row_index, column=week, padx=1, pady=2)  # Minimal padding

                # Save the checkbox variable in the student's weekly attendance record
                self.student_attendances[student_id][week-1] = week_var

            row_index += 1

        # Create a frame for buttons to center them
        button_frame = tk.Frame(self.attendance_frame, background="white")
        button_frame.grid(row=row_index, column=0, columnspan=14, pady=10)

        # Buttons with slightly reduced width
        button_width = 12  # Reduced from 12

        # Back button
        back_btn = ttk.Button(button_frame, style="Blue.TButton", text="Back", 
                            command=self.show_study_frame, width=button_width)
        back_btn.pack(side=tk.LEFT, padx=5)  # Reduced padding

        # Save button
        save_btn = ttk.Button(button_frame, style="Blue.TButton", text="Save", 
                            command=self.save_attendance, width=button_width)
        save_btn.pack(side=tk.LEFT, padx=5)  # Reduced padding
        
        # Previous button (only if not on first page)
        if self.current_page > 0:
            prev_btn = ttk.Button(button_frame, style="Blue.TButton", text="Previous", 
                                command=self.previous_page, width=button_width)
            prev_btn.pack(side=tk.LEFT, padx=5)  # Reduced padding

        # Next button (only if not on last page)
        if self.current_page < self.total_pages - 1:
            next_btn = ttk.Button(button_frame, style="Blue.TButton", text="Next", 
                                command=self.next_page, width=button_width)
            next_btn.pack(side=tk.LEFT, padx=5)  # Reduced padding

        # Add page indicator
        page_label = tk.Label(button_frame, background="white", 
                            text=f"Page {self.current_page + 1} of {self.total_pages}",
                            font=("Arial", 9))  # Smaller font
        page_label.pack(side=tk.LEFT, padx=10)

        # Pack the frame with some padding to keep elements from touching window edges
        self.attendance_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def truncate_name(self, name, max_width):
        """
        Truncate a name to fit within max_width characters and add ellipsis if needed.
        For Arabic names, the ellipsis is added at the beginning instead of the end.

        Args:
            name (str): The original student name
            max_width (int): Maximum number of characters

        Returns:
            str: Truncated name with ellipsis if needed
        """
        if len(name) <= max_width:
            return name
        else:
            # For non-Arabic names, truncate from the end and put ellipsis at the end
            return  '...' + name[:max_width-3]

    def next_page(self):
        """Go to the next page of students."""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_students_page()

    def previous_page(self):
        """Go to the previous page of students."""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_students_page()

    # Clear Frames
    def clear_frame(self, frame):
        """Clears all contents from the specified frame."""
        for widget in frame.winfo_children():
           widget.destroy()

    def clear_frames(self):
        """Clears and unpacks all frames."""
        frames = [
            self.intro_frame, self.mode_selection_frame, self.sign_in_frame, self.classes_frame,
            self.study_frame, self.attendance_taking_method_frame,
            self.select_week_frame, self.camera_frame, self.detection_frame, self.attendance_frame, 
            self.branch_frame
        ]
        for frame in frames:
            self.clear_frame(frame)
            frame.pack_forget()  # Remove frame from display

    # Submit Chosen Class
    def on_submit_chosen_class(self, class_name):
        """Handles submit button click event for chosen class."""
        # Get the list of students who attended
        self.chosen_class_variable = class_name

        # Display the attendance frame
        self.show_branch_frame()
        
    # Submit Study
    def on_submit_study(self):
        """
        Handles the submission of study type selection.
        Updates the study type and transitions to branch selection.
        """
        # Update study type from radio button selection
        self.study_type = self.study_variable.get()

        # Show branch selection frame
        self.show_attendance_taking_method_frame()
    
    def on_submit_branch(self):
        """
        Handles the submission of branch selection.
        Updates the branch type and transitions to attendance frame.
        """
        # Update branch type from radio button selection
        self.branch_type = self.branch_variable.get()

        # Show attendance frame for the selected class, study type, and branch
        self.show_study_frame()

    def on_submit_attendance_method(self):
        """
        Handles the submission of attendance method selection.
        Updates the attendance method and transitions to attendance frame.
        """
        # Update attendance method from radio button selection
        self.attendance_method = self.attendance_method_variable.get()

        # Check if submission method if manual or automatic and proceed accordingly
        if self.attendance_method == "Manual":
            self.show_attendance_frame()
        else:
            self.show_select_week_frame()

    def on_submit_week(self):
        '''
        Handles the submission of week selection.
        '''
        week_str = self.week_variable.get()
        self.week = int(week_str)

        # Proceed to camera selection
        self.show_camera_frame()

    def on_submit_camera(self):
        '''
        Handles the submission of camera selection.
        '''
        camera_str = self.camera_variable.get()
        self.camera_index = int(camera_str.split()[-1])

        # Proceed to the attendance frame
        self.show_detection_frame()
        

    def on_submit_email_password(self):
        """Handles submit button click event for email and password."""
        # Get email and password from entries
        self.email_variable = self.email_entry.get()
        self.password_variable = self.password_entry.get()
    
        # Check email and password validity
        if not check_email_valid(self.email_variable):
            messagebox.showerror("Error", "Invalid email.")
            return
    
        if not check_password_valid(self.password_variable):
            messagebox.showerror("Error", "Invalid password.")
            return
    
        try:
            # Sign in with Firebase Authentication
            user = self.auth.sign_in_with_email_and_password(
                self.email_variable, 
                self.password_variable
            )
    
            # Verify user is not None
            if not user or 'idToken' not in user:
                raise ValueError("Authentication failed. No token received.")
    
            self.token_variable = user.get('idToken')
    
            # Decode the token to get the user_id
            try:
                decoded_token = jwt.decode(self.token_variable, options={"verify_signature": False})
                user_id = decoded_token.get('user_id')
    
                if not user_id:
                    raise ValueError("Could not extract user ID from token")
            except Exception as token_error:
                raise ValueError(f"Token decoding error: {str(token_error)}")
            
            # Create AttendanceManager with the selected local data path
            self.attendance_manager = AttendanceManager(
                database=self.database, 
                lecturer_id=user_id,
                local_data_path=self.json_save_path,
                lecturer_token=self.token_variable
            )
    
            # Handle based on the online mode choice
            if self.online_mode_choice:
                # Existing JSON file scenario
                try:
                    # Load local students
                    self.local_data = self.attendance_manager.load_local_students()
                    
                    # Check if the logged-in user ID matches the stored lecturer ID
                    if not self.local_data or 'lecturer_info' not in self.local_data:
                        raise ValueError("No lecturer information found in the existing JSON file")
                    
                    stored_lecturer_id = self.local_data['lecturer_info'].get('id')
                    
                    if stored_lecturer_id != user_id:
                        raise ValueError("Logged-in user does not match the lecturer in the existing JSON file")
                    
                    # If no exception raised, we can proceed
                    self.lecturer_name_variable = self.local_data['lecturer_info'].get('name', 'Unknown Lecturer')
                    self.lecturer_classes_variable = self.local_data['lecturer_info'].get('classes', [])
                    self.lecturer_id = stored_lecturer_id
                    
                except Exception as e:
                    messagebox.showerror("File Validation Error", str(e))
                    return
            else:
                # New file scenario - fetch and save students
                try:
                    # Fetch students from Firebase
                    self.local_data = self.attendance_manager.fetch_students()
                    
                    # Save students locally
                    self.attendance_manager.save_students_locally()
                    
                    # Set lecturer information from fetched data
                    lecturer_info = self.local_data.get('lecturer_info', {})
                    self.lecturer_name_variable = lecturer_info.get('name', 'Unknown Lecturer')
                    self.lecturer_classes_variable = lecturer_info.get('classes', [])
                    self.lecturer_id = lecturer_info.get('id')
                    
                except Exception as e:
                    messagebox.showerror("Fetch Students Error", str(e))
                    return
    
            # Proceed to classes frame
            self.show_classes_frame()
    
        except Exception as e:
            # Comprehensive error handling
            error_message = str(e)
    
            # Try to extract Firebase-specific error message
            try:
                # Check if error is from Firebase auth
                error_dict = json.loads(e.args[1]) if len(e.args) > 1 else {}
                firebase_error = error_dict.get('error', {}).get('message', '')
                if firebase_error:
                    error_message = firebase_error
            except:
                pass
            
            messagebox.showerror("Authentication Error", error_message)

    def save_attendance(self):
        '''
        Save the attendance data to the local JSON file and optionally upload it to Firebase.
        '''
        try:
            # Validate required attributes
            if not hasattr(self, 'local_data') or not hasattr(self, 'student_attendances'):
                messagebox.showerror("Error", "No attendance data available.")
                return

            # Iterate through student attendances and update local data
            for student_id, attendance_vars in self.student_attendances.items():
                # Convert checkbox variables to integer list
                attendance_list = [int(var.get()) for var in attendance_vars.values()]

                # Navigate through nested structure to find student
                students_data = self.local_data.get("students", {})
                study_type_data = students_data.get(self.study_type, {})
                branch_data = study_type_data.get(self.branch_type, {})
                student_data = branch_data.get(student_id)

                if student_data and "classes" in student_data:
                    # Update attendance for the specific class
                    student_data["classes"][self.chosen_class_variable] = attendance_list
                else:
                    print(f"Warning: Student {student_id} not found in local data")
                    continue
                 
            # Update attendance manager's local students data
            self.attendance_manager.local_students = self.local_data

            # Save to local file
            self.attendance_manager.save_students_locally()

            # Handle online/offline modes
            if self.mode == "online":
                try:
                    self.attendance_manager.upload_local_students()
                    messagebox.showinfo("Success", "Attendance saved and uploaded successfully.")
                except Exception as upload_error:
                    messagebox.showerror("Upload Error", 
                                       f"Attendance saved locally but failed to upload: {upload_error}")
            else:
                messagebox.showinfo("Success", "Attendance saved successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save attendance: {e}")
            print(f"Detailed error: {str(e)}")  # For debugging


# Create and run the Tkinter app
root = tk.Tk()
app = SignInApp(root)
root.mainloop()