import tkinter as tk
from tkinter import ttk
import firebase_admin as fb
import json
from firebase_admin import credentials, db
from tkinter import messagebox
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from GeneralUtilities.UtilityChecks import check_branch_valid, check_stage_valid, check_semester_valid, check_class_exists, check_class_name_valid

# Function to add a class to the database
def add_class(class_name, branches, stage, semesters, database):
    # Validate input fields
    if not check_class_name_valid(class_name):
        raise ValueError("Invalid class name")
    if check_class_exists(class_name, database):
        raise ValueError(f"Class {class_name} already exists")
    if not check_branch_valid(branches):
        raise ValueError("Invalid branch")
    if not check_stage_valid(stage):
        raise ValueError("Invalid stage")
    if not check_semester_valid(semesters):
        raise ValueError("Invalid semester")

    # Set data in the database
    database.reference('/').child(f"Classes/{class_name}").set({
        'branch': branches,
        'stage': stage,
        'semester': semesters
    })
    print(f"Class {class_name} added successfully")
    return

# Define a class for the Add Class GUI
class AddClassApp:
    def __init__(self, root, database):
        self.root = root
        self.root.title("Add Class")

        self.script_dir = os.path.dirname(os.path.abspath(__file__))  # path to script
        image_path = os.path.join(self.script_dir, "..", "resources", "Icon.ico")
        image_path = os.path.abspath(image_path)

        self.database = database
        self.root.iconbitmap(image_path)  # Set the icon for the window

        # Check if Firebase database is initialized
        if not self.database:
            messagebox.showerror("Error", "Failed to initialize Firebase database")
            self.root.destroy()
            return
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

        # Set window size and center it
        window_width = 450
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)
        self.root.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")

        # Frame for adding class information
        self.add_class_frame = tk.Frame(self.root,bg="white")
        self.add_class_frame.pack(pady=20)

        # Class name input
        tk.Label(self.add_class_frame,background="white", text="Class Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.class_name_entry = tk.Entry(self.add_class_frame, width=25)
        self.class_name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Stage selector (1,2,3,4)
        tk.Label(self.add_class_frame,background="white", text="Stage:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.stage_variable = tk.StringVar(value="1")
        stage_options = ["1", "2", "3", "4"]
        self.stage_selector = ttk.OptionMenu(self.add_class_frame, self.stage_variable, *stage_options, style='Custom.TMenubutton')
        self.stage_selector.config(width=10)
        self.stage_selector.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Branch selector (IT, NE - multiple selection)
        tk.Label(self.add_class_frame,background="white", text="Branch:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        branches_frame = tk.Frame(self.add_class_frame, bg="white")
        branches_frame.grid(row=2, column=1, sticky="w")
        self.branch_it_var = tk.IntVar()
        self.branch_ne_var = tk.IntVar()
        tk.Checkbutton(branches_frame, text="IT", variable=self.branch_it_var,background="white").pack(side="left", padx=2)
        tk.Checkbutton(branches_frame, text="NE", variable=self.branch_ne_var,background="white").pack(side="left", padx=2)

        # Semester selector (1, 2 - multiple selection)
        tk.Label(self.add_class_frame,background="white", text="Semester:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        semesters_frame = tk.Frame(self.add_class_frame, bg="white")
        semesters_frame.grid(row=3, column=1, sticky="w")
        self.semester_1_var = tk.IntVar()
        self.semester_2_var = tk.IntVar()
        tk.Checkbutton(semesters_frame, text="1", variable=self.semester_1_var,background="white").pack(side="left", padx=2)
        tk.Checkbutton(semesters_frame, text="2", variable=self.semester_2_var,background="white").pack(side="left", padx=2)

        # Submit button
        submit_button = ttk.Button(self.add_class_frame,style="Blue.TButton", text="Add Class", command=self.submit_class)
        submit_button.grid(row=4, column=0, columnspan=2, pady=15)

    def submit_class(self):
        """Handles the submission of class details and saves them to the Firebase database."""
        class_name = self.class_name_entry.get().strip()
        stage = self.stage_variable.get()

        # Collect selected branches
        branches = {}
        if self.branch_it_var.get():
            branches['IT'] = True
        if self.branch_ne_var.get():
            branches['NE'] = True

        # Collect selected semesters
        semesters = {}
        if self.semester_1_var.get():
            semesters['1'] = True
        if self.semester_2_var.get():
            semesters['2'] = True

        # Error handling
        try:
            add_class(class_name, branches, stage, semesters, self.database)
            messagebox.showinfo("Success", "Class added successfully.")
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add class: {str(e)}")

    def clear_inputs(self):
        """Clears the input fields after submission."""
        self.class_name_entry.delete(0, tk.END)
        self.stage_variable.set("1")
        self.branch_it_var.set(0)
        self.branch_ne_var.set(0)
        self.semester_1_var.set(0)
        self.semester_2_var.set(0)