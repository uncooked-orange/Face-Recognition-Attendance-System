import tkinter as tk
from tkinter import messagebox
import firebase_admin as fb
import json
from firebase_admin import credentials, db
from UtilityChecks import check_branch_valid, check_stage_valid, check_semester_valid, check_class_exists, check_class_name_valid

firebase_credentials_user = json.load(open("UserCredentials.json", "r"))
database_credential = {"databaseURL" : firebase_credentials_user["databaseURL"]}

# Initialize Firebase
def initialize_firebase():
    try:
        cred = credentials.Certificate("AdminCredentials.json")
        fb.initialize_app(cred, database_credential)
        return db
    except Exception as e:
        print(f"Failed to initialize Firebase: {str(e)}")
        return None

database = initialize_firebase()

# Function to add a class to the database
def add_class(class_name, branches, stage, semesters, database_ref):
    # Validate input fields
    if not check_class_name_valid(class_name):
        raise ValueError("Invalid class name")
    if check_class_exists(class_name, database_ref):
        raise ValueError(f"Class {class_name} already exists")
    if not check_branch_valid(branches):
        raise ValueError("Invalid branch")
    if not check_stage_valid(stage):
        raise ValueError("Invalid stage")
    if not check_semester_valid(semesters):
        raise ValueError("Invalid semester")

    # Set data in the database
    database_ref.reference('/').child(f"Classes/{class_name}").set({
        'branch': branches,
        'stage': stage,
        'semester': semesters
    })
    print(f"Class {class_name} added successfully")
    return

# Define a class for the Add Class GUI
class AddClassApp:
    def __init__(self, root, database_ref=database):
        self.root = root
        self.root.title("Add Class")
        self.database = database_ref

        if not self.database:
            messagebox.showerror("Error", "Failed to initialize Firebase database")
            self.root.destroy()
            return

        # Set window size and center it
        window_width = 400
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)
        self.root.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")

        # Frame for adding class information
        self.add_class_frame = tk.Frame(self.root)
        self.add_class_frame.pack(pady=20)

        # Class name input
        tk.Label(self.add_class_frame, text="Class Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.class_name_entry = tk.Entry(self.add_class_frame, width=25)
        self.class_name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Stage selector (1,2,3,4)
        tk.Label(self.add_class_frame, text="Stage:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.stage_variable = tk.StringVar(value="1")
        stage_options = ["1", "2", "3", "4"]
        self.stage_selector = tk.OptionMenu(self.add_class_frame, self.stage_variable, *stage_options)
        self.stage_selector.config(width=10)
        self.stage_selector.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Branch selector (IT, NE - multiple selection)
        tk.Label(self.add_class_frame, text="Branch:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        branches_frame = tk.Frame(self.add_class_frame)
        branches_frame.grid(row=2, column=1, sticky="w")
        self.branch_it_var = tk.IntVar()
        self.branch_ne_var = tk.IntVar()
        tk.Checkbutton(branches_frame, text="IT", variable=self.branch_it_var).pack(side="left", padx=2)
        tk.Checkbutton(branches_frame, text="NE", variable=self.branch_ne_var).pack(side="left", padx=2)

        # Semester selector (1, 2 - multiple selection)
        tk.Label(self.add_class_frame, text="Semester:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        semesters_frame = tk.Frame(self.add_class_frame)
        semesters_frame.grid(row=3, column=1, sticky="w")
        self.semester_1_var = tk.IntVar()
        self.semester_2_var = tk.IntVar()
        tk.Checkbutton(semesters_frame, text="1", variable=self.semester_1_var).pack(side="left", padx=2)
        tk.Checkbutton(semesters_frame, text="2", variable=self.semester_2_var).pack(side="left", padx=2)

        # Submit button
        submit_button = tk.Button(self.add_class_frame, text="Add Class", command=self.submit_class)
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

# Create and run the AddClassApp in a standalone Tkinter window
root = tk.Tk()
app = AddClassApp(root, database)
root.mainloop()
