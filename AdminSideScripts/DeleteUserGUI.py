import tkinter as tk
from tkinter import messagebox, ttk
import firebase_admin as fb
from firebase_admin import credentials, auth, db
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from GeneralUtilities.UtilityChecks import check_email_valid, check_user_exists

# Fetch user name before deletion
def fetch_user_name(Email, database, auth):
    try:
        # check if email is valid
        if not check_email_valid(Email):
            raise ValueError("Invalid Email")

        # check if user exists
        if not check_user_exists(Email, auth):
            raise ValueError("User does not exist")

        # get user
        user = auth.get_user_by_email(Email)

        # get Role from custom claims
        Role = user.custom_claims.get('role')

        # fetch user name from database
        name_ref = database.reference(f'/{Role}s/{user.uid}/Name')
        name = name_ref.get()

        return name, Role, user.uid

    except Exception as e:
        print(f"Error fetching user name: {e}")
        return None, None, None

# Delete a user
def delete_user(Email, database, auth):
    try:
        # check if email is valid
        if not check_email_valid(Email):
            raise ValueError("Invalid Email")

        # check if user exists
        if not check_user_exists(Email, auth):
            raise ValueError("User does not exist")

        # get user
        user = auth.get_user_by_email(Email)

        # get Role from custom claims
        Role = user.custom_claims.get('role')

        # delete user
        auth.delete_user(user.uid)
        print(f"Successfully deleted user: {user.uid} from authentication server")

        # delete user from database
        database.reference('/').child(f"{Role}s").child(user.uid).delete()
        print(f"Successfully deleted user: {user.uid} from database")

    except Exception as e:
        print(f"Error deleting user: {e}")
        raise

# Define a class for the Delete User GUI
class DeleteUserGUI:
    def __init__(self, root, database, auth):
        self.root = root
        self.root.title("Delete User")
        
        self.database = database
        self.Auth = auth
        

        # Configure root window
        self.root.configure(bg='white')

        # Set window size and center it
        window_width = 600
        window_height = 350

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.script_dir = os.path.dirname(os.path.abspath(__file__))  # path to script
        image_path = os.path.join(self.script_dir, "..", "resources", "Icon.ico")
        image_path = os.path.abspath(image_path)

        self.main_image_path = os.path.join(self.script_dir, "..", "resources", "MainImage.png")
        self.main_image_path = os.path.abspath(self.main_image_path)

        self.root.iconbitmap(image_path)  # Set the icon for the window

        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)

        self.root.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")

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

        # Create main frame with blue and white styling
        self.frame = tk.Frame(self.root, bg='white')
        self.frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Create a title label
        self.label = tk.Label(self.frame, 
                               text="Delete User", 
                               font=("Arial", 20, "bold"), 
                               fg='#2C3E50', 
                               bg='white')
        self.label.pack(pady=(0, 20))

        # Create a label for the email
        self.email_label = tk.Label(self.frame, 
                                    text="Email", 
                                    font=("Arial", 12), 
                                    fg='#2C3E50', 
                                    bg='white')
        self.email_label.pack()

        # Create an entry for the email with styled entry
        self.email_entry = ttk.Entry(self.frame, 
                                     width=30, 
                                     style='Custom.TEntry')
        self.email_entry.pack(pady=10)

        # Create a confirmation label
        self.confirm_label = tk.Label(self.frame, 
                                      text="", 
                                      font=("Arial", 10), 
                                      fg='#2C3E50', 
                                      bg='white')
        self.confirm_label.pack(pady=10)

        # Create a button to submit email
        self.submit_button = ttk.Button(self.frame, 
                                        text="Submit", 
                                        command=self.check_user, 
                                        style='Blue.TButton',
                                        width=20)
        self.submit_button.pack(pady=10)

        # Create a button to delete the user
        self.delete_button = ttk.Button(self.frame, 
                                        text="Confirm Delete", 
                                        command=self.delete_user, 
                                        style='Blue.TButton',
                                        width=20)
        self.delete_button.pack(pady=10)
        self.delete_button.pack_forget()  # Initially hidden

        # Store user details
        self.user_name = None
        self.user_role = None
        self.user_id = None

    # Function to check user before deletion
    def check_user(self):
        try:
            # Get the email from the entry
            Email = self.email_entry.get()
            
            # Fetch user name
            self.user_name, self.user_role, self.user_id = fetch_user_name(Email, self.database, self.Auth)
            
            if self.user_name:
                # Update confirmation label
                confirm_text = f"Found User: {self.user_name} ({self.user_role})\n"
                confirm_text += "Are you sure you want to delete this user?"
                self.confirm_label.config(text=confirm_text)
                
                # Show delete button, hide submit button
                self.submit_button.pack_forget()
                self.delete_button.pack(pady=10)
            else:
                messagebox.showerror("Error", "User not found")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error checking user: {str(e)}")

    # Function to delete the user
    def delete_user(self):
        try:
            # Get the email from the entry
            Email = self.email_entry.get()
            
            # Delete the user
            delete_user(Email, self.database, self.Auth)
            
            # Show a success message
            messagebox.showinfo("Success", f"User {self.user_name} deleted successfully")
            
            # Reset the GUI
            self.email_entry.delete(0, tk.END)
            self.confirm_label.config(text="")
            self.delete_button.pack_forget()
            self.submit_button.pack(pady=10)
            
            # Reset user details
            self.user_name = None
            self.user_role = None
            self.user_id = None
        
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting user: {str(e)}")
