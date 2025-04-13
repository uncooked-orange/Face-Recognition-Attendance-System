import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import filedialog,ttk
from PIL import Image, ImageTk
import firebase_admin as fb
import json
from firebase_admin import credentials, db, auth
import cv2
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from AdminUtilities.SignUp import sign_up_lecturer, sign_up_student
from GeneralUtilities.UtilityChecks import check_student_info
from GeneralUtilities.Detection import FaceRecognitionSystem

# Define a class for the SignUp GUI
class SignUpApp:
    def __init__(self, root, database, Auth):
        self.root = root
        self.root.title("Sign Up")

        self.database = database
        self.Auth = Auth
        self.face_image_path = None  # Initialize face image path

        # Set window size and center it
        window_width = 600
        window_height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = (screen_width / 2) - (window_width / 2)
        self.y = (screen_height / 2) - (window_height / 2)
        self.root.geometry(f"{window_width}x{window_height}+{int(self.x)}+{int(self.y)}")

        self.script_dir = os.path.dirname(os.path.abspath(__file__))  # path to script
        image_path = os.path.join(self.script_dir, "..", "resources", "Icon.ico")
        image_path = os.path.abspath(image_path)

        self.root.iconbitmap(image_path)  # Set the icon for the window
        
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

        
        # Show the role selection frame first
        self.show_role_selection_frame()

    def show_role_selection_frame(self):
        '''Display the role selection frame for the user to select a role.'''
        # Clear existing frames
        for widget in self.root.winfo_children():
            widget.destroy()

        # Role variable
        self.role_variable = tk.StringVar("")
        
        # Role selection frame
        frame = tk.Frame(self.root,bg="white")
        frame.pack(pady=20, padx=20)

        tk.Label(frame, text="Select Which Role To Create An Account For", font=("Arial", 14), background="white").pack(pady=10)
        
        # Radiobuttons for selecting role and set default value to Student
        self.role_variable.set("Student")
        tk.Radiobutton(frame, text="Student", variable=self.role_variable, value="Student", background="white").pack(pady=5)
        tk.Radiobutton(frame, text="Lecturer", variable=self.role_variable, value="Lecturer", background="white").pack(pady=5)

        # Submit button
        ttk.Button(frame, text="Submit", command=self.submit_role,style="Blue.TButton").pack(pady=10)

    def submit_role(self):
        '''Submit the selected role and show the corresponding sign-up frame.'''

        # Get the selected role
        role = self.role_variable.get()
       
        # Show frame based on the selected role
        if role == "Student":
            self.show_student_signup_frame()
        elif role == "Lecturer":
            self.show_lecturer_signup_frame()

    def show_student_signup_frame(self):
        '''Display the student sign-up frame for the student to enter details.'''
        # Clear existing frames
        for widget in self.root.winfo_children():
            widget.destroy()

        # Student sign-up frame
        frame = tk.Frame(self.root,bg="white")
        frame.pack(pady=20, padx=20)


        # Email, Password, Confirm Password, Name, Branch, Study, Stage variables
        self.email_variable = tk.StringVar()
        self.password_variable = tk.StringVar()
        self.confirm_password_variable = tk.StringVar()
        self.name_variable = tk.StringVar()
        self.branch_variable = tk.StringVar()
        self.study_variable = tk.StringVar()
        self.stage_variable = tk.StringVar()

        # Title
        tk.Label(frame,background="white", text="Student Sign-Up", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=10)

        # Email input
        tk.Label(frame,background="white", text="Email:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(frame, textvariable=self.email_variable).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Password input
        tk.Label(frame,background="white", text="Password:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(frame, show="*", textvariable=self.password_variable).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Password input
        tk.Label(frame,background="white", text="Confirm Password:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(frame, show="*", textvariable=self.confirm_password_variable).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # Name input
        tk.Label(frame,background="white", text="Name:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(frame, textvariable=self.name_variable).grid(row=4, column=1, sticky="w", padx=5, pady=5)

        # Branch input Radio buttons
        self.branch_variable.set("IT")
        tk.Label(frame,background="white", text="Branch:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        branch_frame = tk.Frame(frame,background="white")
        branch_frame.grid(row=5, column=1, sticky="w", padx=5)
        tk.Radiobutton(branch_frame,background="white", text="IT", variable=self.branch_variable, value="IT").pack(side="left", padx=5)
        tk.Radiobutton(branch_frame,background="white", text="NE", variable=self.branch_variable, value="NE").pack(side="left", padx=5)

        # Study input Radio buttons
        self.study_variable.set("Morning")  
        tk.Label(frame,background="white", text="Study:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        study_frame = tk.Frame(frame,background="white")
        study_frame.grid(row=6, column=1, sticky="w", padx=5)
        tk.Radiobutton(study_frame,background="white", text="Morning", variable=self.study_variable, value="Morning").pack(side="left", padx=5)
        tk.Radiobutton(study_frame,background="white", text="Evening", variable=self.study_variable, value="Evening").pack(side="left", padx=5)

        # Stage input Radio buttons
        self.stage_variable.set("1")
        tk.Label(frame,background="white", text="Stage:").grid(row=7, column=0, sticky="e", padx=5, pady=5)
        stage_frame = tk.Frame(frame,background="white")
        stage_frame.grid(row=7, column=1, sticky="w", padx=5)
        for stage in range(1, 5):
            tk.Radiobutton(stage_frame,background="white", text=str(stage), variable=self.stage_variable, value=str(stage)).pack(side="left", padx=5)


        # Submit and Back buttons
        button_frame = tk.Frame(frame,background="white")
        button_frame.grid(row=8, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame,style="Blue.TButton", text="Back", command=self.show_role_selection_frame).pack(side="left", padx=10)
        ttk.Button(button_frame,style="Blue.TButton", text="Submit", command=self.submit_student_info).pack(side="left", padx=10)

    def show_student_image_upload_frame(self):
        '''Display the student image upload frame for the student to upload multiple images.'''
        # Clear existing frames
        for widget in self.root.winfo_children():
            widget.destroy()

        # Initialize embeddings list if not exists
        if not hasattr(self, "embeddings_list"):
            self.embeddings_list = []
            self.uploaded_images_count = 0

        # Student image upload frame
        frame = tk.Frame(self.root, bg="white")
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Title
        tk.Label(frame, background="white", text=f"Upload Images for {self.student_data['Name']}", 
                 font=("Arial", 14)).pack(pady=10)

        # Status label
        status_text = f"Uploaded {self.uploaded_images_count}/5 images"
        self.status_label = tk.Label(frame, background="white", text=status_text, font=("Arial", 12))
        self.status_label.pack(pady=5)

        # Image Upload Button and Preview
        image_button = ttk.Button(frame, style="Blue.TButton", text="Select Image", 
                                 command=self.upload_and_process_image)
        image_button.pack(pady=5)

        # Placeholder for Image Preview
        self.image_preview_label = tk.Label(frame, background="white")
        self.image_preview_label.pack(pady=10)

        # Image thumbnails frame
        thumbnails_frame = tk.Frame(frame, background="white")
        thumbnails_frame.pack(pady=10, fill="x")

        # Create thumbnail labels for each image
        self.thumbnail_labels = []
        for i in range(5):
            # Create a frame with a border to represent an image slot
            slot_frame = tk.Frame(thumbnails_frame, bg="lightgray", width=100, height=100, bd=2, relief="groove")
            slot_frame.pack(side="left", padx=5)
            slot_frame.pack_propagate(False)  # Prevent the frame from resizing

            # Add label inside the frame
            thumbnail_label = tk.Label(slot_frame, bg="lightgray", text=f"Image {i+1}")
            thumbnail_label.pack(expand=True)
            self.thumbnail_labels.append(thumbnail_label)

        # Submit and Back buttons
        button_frame = tk.Frame(frame, background="white")
        button_frame.pack(pady=20)
        ttk.Button(button_frame, style="Blue.TButton", text="Back", 
                  command=self.show_student_signup_frame).pack(side="left", padx=10)

        # Submit button - enabled only when 5 images are uploaded
        self.submit_button = ttk.Button(button_frame, style="Blue.TButton", text="Submit", 
                                       command=self.submit_student, state="disabled")
        self.submit_button.pack(side="left", padx=10)

        # Enable submit button if already have 5 images
        if self.uploaded_images_count >= 5:
            self.submit_button.config(state="normal")

    def show_lecturer_signup_frame(self):
        '''Display the lecturer sign-up frame for the lecturer to select stages'''
        # Clear existing frames
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Email, Password,Confirm Password, Name variables
        self.email_variable = tk.StringVar()
        self.password_variable = tk.StringVar()
        self.confirm_password_variable = tk.StringVar()
        self.name_variable = tk.StringVar()
        self.lecturer_stages_variables = []
        self.selected_classes = []
        
        # Set default values
        #self.email_variable.set("fhdsaj@fdshal.com")
        #self.password_variable.set("password")
        #self.confirm_password_variable.set("password")
        #self.name_variable.set("John Doe")

        # Lecturer sign-up frame
        frame = tk.Frame(self.root,bg="white")
        frame.pack(pady=30, padx=30)

        tk.Label(frame,background="white", text="Lecturer Sign-Up", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Email input
        tk.Label(frame,background="white", text="Email:").grid(row=1, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.email_variable).grid(row=1, column=1, sticky="w")

        # Password input
        tk.Label(frame,background="white", text="Password:").grid(row=3, column=0, sticky="w")
        tk.Entry(frame, show="*", textvariable=self.password_variable).grid(row=3, column=1, sticky="w")

        # Password input
        tk.Label(frame,background="white", text="Confirm Password:").grid(row=4, column=0, sticky="w")
        tk.Entry(frame, show="*", textvariable=self.confirm_password_variable).grid(row=4, column=1, sticky="w")

        # Name input
        tk.Label(frame,background="white", text="Name:").grid(row=5, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.name_variable).grid(row=5, column=1, sticky="w")
        
        # Stages selection
        tk.Label(frame,background="white", text="Stages Taught:").grid(row=6, column=0, sticky="w")
        stages_frame = tk.Frame(frame,background="white")
        stages_frame.grid(row=6, column=1, sticky="w", padx=5)
        for stage in range(1, 5):
            var = tk.StringVar(value="")  # Initialize empty to deselect by default
            self.lecturer_stages_variables.append([str(stage), var])
            tk.Checkbutton(stages_frame,background="white", text=str(stage), variable=var, onvalue=str(stage), offvalue="").pack(side="left")

        ## Branches selection
        #tk.Label(frame, text="Branches:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        #branches_frame = tk.Frame(frame)
        #branches_frame.grid(row=5, column=1, sticky="w", padx=5)
        #for branch in ["IT", "NE"]:
        #    var = tk.StringVar(value="")  # Initialize empty to deselect by default
        #    self.lecturer_branches_variables.append([branch, var])
        #    tk.Checkbutton(branches_frame, text=branch, variable=var, onvalue=branch, offvalue="").pack(side="left", padx=5)

        # Submit and Back buttons
        button_frame = tk.Frame(frame,background="white")
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame,style="Blue.TButton", text="Back", command=self.show_role_selection_frame).pack(side="left", padx=10)
        ttk.Button(button_frame,style="Blue.TButton", text="Submit", command=self.submit_lecturer_stages).pack(side="left", padx=10)
    
    def show_class_selection_frame(self):
        '''Display the class selection frame for the lecturer to select classes.'''
        # Clear existing frames
        for widget in self.root.winfo_children():
            widget.destroy()
    
        # Initialize the selected_classes list
        self.selected_classes = []
    
        # Canvas
        canvas = tk.Canvas(self.root, borderwidth=0, background="white")
        canvas.pack(side="top", fill="both", expand=True)
    
        # Create a scrollbar that controls the canvas
        scrollbar = tk.Scrollbar(canvas,background="white", orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
    
        # Configure the canvas to work with the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
    
        # Class selection frame inside the canvas
        frame = tk.Frame(canvas,background="white")
    
        # Place the frame in the canvas and center it
        canvas.create_window((canvas.winfo_width() / 2, 0), window=frame, anchor="n")
    
        # Update scroll region when the frame changes size
        frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
    
        # Display the classes
        count = 0
        max_classes_per_row = 2  # Set the maximum number of checkboxes per row
    
        for stage, classes in sorted(self.classes_by_stage_dict.items()):
            # Add stage title
            stage_label = tk.Label(frame,background="white", text=f"Stage {stage}", font=("Arial", 10, "bold"))
            stage_label.grid(row=count, column=0, sticky="w", pady=(10, 5))
            count += 1
    
            # Display each class under the stage title, wrapping rows after max_classes_per_row
            col = 1  # Start column for checkboxes next to stage title
            row = count  # Track the current row for the checkboxes
    
            for index, class_name in enumerate(classes):
                # Create a variable for each class and store it in the dictionary
                var = tk.BooleanVar()
    
                # Update selected_classes based on checkbox status
                def toggle_selection(class_name=class_name, var=var):
                    if var.get():
                        self.selected_classes.append(class_name)
                    else:
                        self.selected_classes.remove(class_name)
    
                # Create a checkbox and bind it to toggle_selection
                checkbox = tk.Checkbutton(frame,background="white", text=class_name, variable=var, command=toggle_selection)
                checkbox.grid(row=row, column=col, sticky="w", padx=15, pady=2)
    
                # Move to the next column
                col += 1
    
                # If max_classes_per_row is reached, reset to the next row and start from the first column
                if (index + 1) % max_classes_per_row == 0:
                    row += 1
                    col = 1
    
            # Update count to the next row for the next stage's label
            count = row + 1
    
        # Submit and Back buttons
        button_frame = tk.Frame(frame,background="white")
        button_frame.grid(row=count, column=1, columnspan=2, pady=10)
    
        # Center the buttons using grid
        ttk.Button(button_frame,style="Blue.TButton", text="Back", command=self.show_lecturer_signup_frame).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame,style="Blue.TButton", text="Submit", command=self.submit_lecturer).grid(row=0, column=1, padx=10)
    
        # Configure the button frame to center its contents
        button_frame.grid_columnconfigure(0, weight=1)  # Allow first column to expand
        button_frame.grid_columnconfigure(1, weight=1)  # Allow second column to expand
    
        # Set up canvas scrolling with the mouse wheel
        canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas = canvas  # Store reference to canvas for mousewheel function

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def upload_image(self):
        '''Allow the student to upload a face image.'''
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.face_image_path = file_path
            
            # Load and preview the image
            print(self.face_image_path)
            self.student_image = Image.open(file_path)
            self.student_image.thumbnail((200, 200))  # Resize image for preview
            photo = ImageTk.PhotoImage(self.student_image)

            # Update the image preview
            self.image_preview_label.config(image=photo)
            self.image_preview_label.image = photo


    def submit_student_info(self):
        '''Submit the student details and show the class selection frame.'''

        # Collect student data
        self.student_data = {
            "email": self.email_variable.get(),
            "Name": self.name_variable.get(),
            "password": self.password_variable.get(),
            "confirm_password": self.confirm_password_variable.get(),
            "branch": self.branch_variable.get(),
            "study": self.study_variable.get(),
            "stage": self.stage_variable.get()
        }

        # Temporary student data
        #self.student_data = {
        #    "email": "student@s4.com",
        #    "password": "password",
        #    "confirm_password": "password",
        #    "Name": "John Doe",
        #    "branch": "IT",
        #    "study": "Morning",
        #    "stage": "1"
        #}
        #print(self.student_data)

        # Check if student info is valid
        try:
            check_student_info(self.student_data["email"], self.student_data["password"], self.student_data["confirm_password"], self.student_data["Name"], self.student_data["stage"], self.student_data["branch"], self.student_data["study"])
            messagebox.showinfo("Success", "Student data submitted.")
            self.show_student_image_upload_frame()
        except Exception as e:
            print(f"Invalid student info: {str(e)}")
            messagebox.showerror("Error", f"Invalid student info: {str(e)}")
            self.show_student_signup_frame()

    def upload_and_process_image(self):
        '''Upload an image and process it to extract facial embedding'''
        if self.uploaded_images_count >= 5:
            messagebox.showinfo("Info", "You've already uploaded 5 images. You can submit now.")
            return

        # Open file dialog to select image
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=(("Image files", "*.jpg;*.jpeg;*.png"), ("All files", "*.*"))
        )

        if not file_path:
            return  # User cancelled

        self.face_image_path = file_path

        # Process the image to extract embedding
        try:
            # Load the face recognition system
            face_recognition_system = FaceRecognitionSystem()

            # Load the image
            image = cv2.imread(self.face_image_path)

            # Resize image for display
            display_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            display_image = Image.fromarray(display_image)
            display_image = display_image.resize((200, 200), Image.LANCZOS)
            display_photo = ImageTk.PhotoImage(display_image)

            # Update preview
            self.image_preview_label.config(image=display_photo)
            self.image_preview_label.image = display_photo

            # Check if image contains a face
            faces = face_recognition_system.detect_faces(image)
            if faces.size == 0 or len(faces) == 0:
                messagebox.showwarning("Warning", "No face detected in the image.")
                return

            # Check if there is more than one face in the image
            if len(faces) > 1:
                messagebox.showwarning("Warning", "Multiple faces detected in the image.")
                return

            # Align the face
            aligned_face = face_recognition_system.align_face(image, faces[0])

            # Check face quality
            if not face_recognition_system.assess_face_quality(aligned_face):
                messagebox.showwarning("Warning", "The image quality is too low. Please upload a clearer image with good lighting.")
                return

            # Extract features
            embedding = face_recognition_system.extract_features(aligned_face)

            # Add the embedding to our list
            self.embeddings_list.append(embedding)
            self.uploaded_images_count += 1

            # Update the status label
            self.status_label.config(text=f"Uploaded {self.uploaded_images_count}/5 images")

            # Update the thumbnail
            thumbnail_img = cv2.resize(aligned_face, (90, 90))
            thumbnail_img = cv2.cvtColor(thumbnail_img, cv2.COLOR_BGR2RGB)
            thumbnail_img = Image.fromarray(thumbnail_img)
            thumbnail_photo = ImageTk.PhotoImage(thumbnail_img)

            # Update the corresponding thumbnail label
            current_idx = self.uploaded_images_count - 1
            self.thumbnail_labels[current_idx].config(image=thumbnail_photo, text="")
            self.thumbnail_labels[current_idx].image = thumbnail_photo

            # Enable submit button if we have 5 images
            if self.uploaded_images_count >= 2:
                self.submit_button.config(state="normal")
                messagebox.showinfo("Success", "All 5 images uploaded successfully. You can now submit.")

        except Exception as e:
            print(f"Error processing image: {str(e)}")
            messagebox.showerror("Error", f"Failed to process image: {str(e)}")

    
    def submit_student(self):
        '''Submit the student data and all embeddings to the database.'''
        # Check if we have 5 images
        if not hasattr(self, "embeddings_list") or len(self.embeddings_list) < 2:
            messagebox.showwarning("Warning", "Please upload at least 2 images before submitting.")
            self.uploaded_images_count = 0
            self.show_student_image_upload_frame()
            return

        # Add all embeddings to student data
        self.student_data["embeddings"] = self.embeddings_list

        # Sign up student
        try:
            sign_up_student(self.student_data["email"],
                          self.student_data["password"],
                          self.student_data["Name"],
                          self.student_data["study"],
                          self.student_data["stage"],
                          self.student_data["branch"],
                          self.student_data["embeddings"],  # Now sending the list of embeddings
                          self.database,
                          self.Auth)
            messagebox.showinfo("Success", "Student data submitted with 5 face images.")

            # Reset for next student
            self.embeddings_list = []
            self.uploaded_images_count = 0

            self.show_role_selection_frame()
        except Exception as e:
            print(f"Failed to sign up student: {str(e)}")
            messagebox.showerror("Error", "Failed to sign up student.")
            return


    def submit_lecturer_stages(self):
        # Check if email, password, name are valid
        if not self.email_variable.get():
            messagebox.showwarning("Warning", "Please enter an email.")
            self.show_lecturer_signup_frame()
            return
        if not self.password_variable.get():
            messagebox.showwarning("Warning", "Please enter a password.")
            self.show_lecturer_signup_frame()
            return
        if not self.name_variable.get():
            messagebox.showwarning("Warning", "Please enter a name.")
            self.show_lecturer_signup_frame()
            return
        # Check if any stage is selected
        if not any([stage[1].get() for stage in self.lecturer_stages_variables]):
            messagebox.showwarning("Warning", "Please select at least one stage.")
            self.show_lecturer_signup_frame()
            return
        # Collect lecturer data
        lecturer_data = {
            "email": self.email_variable.get(),
            "Name": self.name_variable.get(),
            "stages": [stage[0] for stage in self.lecturer_stages_variables if stage[1].get()],
        }
        
        # Get Classes from the database according to the selected branches and stages
        self.classes_by_stage_dict = {}
        try:
            classes = self.database.reference("/").child("Classes").get()
            if classes:
                for class_id, class_data in classes.items():
                    stage = str(class_data["stage"])
                    if stage in lecturer_data["stages"]:
                        if stage not in self.classes_by_stage_dict:
                            self.classes_by_stage_dict[stage] = []
                        self.classes_by_stage_dict[stage].append(class_id)

        except Exception as e:
            print(f"Failed to fetch classes: {str(e)}")
            messagebox.showerror("Error", "Failed to fetch classes.")
            return
    
        print(self.selected_classes)

        # Go to class selection frame
        self.show_class_selection_frame()

    # Submit lecturer data
    def submit_lecturer(self):
        # Submit lecturer data
        try:
            sign_up_lecturer(self.email_variable.get(), self.password_variable.get(), self.selected_classes, self.name_variable.get(), self.database, self.Auth)
            messagebox.showinfo("Success", "Lecturer data submitted.")
        except Exception as e:
            print(f"Failed to sign up lecturer: {str(e)}")
            messagebox.showerror("Error", "Failed to sign up lecturer.")
        # Go back to role selection frame
        self.show_role_selection_frame()
        return