import tkinter as tk
from tkinter import messagebox
import firebase_admin as fb
from firebase_admin import credentials,auth,db
import json
from UtilityChecks import check_email_valid, check_user_exists

# Get database URL from UserCredentials.json
firebase_credentials_user = json.load(open("UserCredentials.json", "r"))
database_credential = {"databaseURL" : firebase_credentials_user["databaseURL"]}

# Initialize Firebase
cred = credentials.Certificate("AdminCredentials.json")
fb.initialize_app(cred,database_credential)

# get database reference
Database = db
Auth = auth

# Delete a user
def delete_user(Email, database, auth):
    try:
        # check if email is valid
        if not check_email_valid(Email):
            raise ValueError("Invalid Email")

        # check if user exists
        if not check_user_exists(Email,auth):
            raise ValueError("User does not exist")

        # get user
        user = auth.get_user_by_email(Email)

        # get Role from custom claims
        Role = user.custom_claims.get('role')

        # delete user
        auth.delete_user(user.uid)
        print("Successfully deleted user: {0} from authentication server".format(user.uid))

        # delete user from database
        database.reference('/').child("{0}s".format(Role)).child(user.uid).delete()
        print("Successfully deleted user: {0} from database".format(user.uid))

    except Exception as e:
        print("Error deleting user: {0}".format(e))
        return


# Define a class for the Delete User GUI
class DeleteUserGUI:
    def __init__(self, root):
        self.root = root

        # Set window size and center it
        window_width = 400
        window_height = 200

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)

        self.root.geometry("%dx%d+%d+%d" % (window_width, window_height, x, y))

        # Initialize the frames
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        # Create a label
        self.label = tk.Label(self.frame, text="Delete User", font=("Arial", 20))
        self.label.pack(pady=20)

        # Create a label for the email
        self.email_label = tk.Label(self.frame, text="Email")
        self.email_label.pack()

        # Create an entry for the email
        self.email_entry = tk.Entry(self.frame)
        self.email_entry.pack(pady=10)

        # Create a button to delete the user
        self.delete_button = tk.Button(self.frame, text="Submit", command=self.delete_user)
        self.delete_button.pack(pady=20)

        # Create a button to go back to the main menu
        self.back_button = tk.Button(self.frame, text="Back", command=self.back)
        self.back_button.pack()

    # Function to delete the user
    def delete_user(self):
        try:
            # Get the email from the entry
            Email = self.email_entry.get()
            # Delete the user
            delete_user(Email, Database, Auth)
            # Show a success message
            messagebox.showinfo("Success", "User deleted successfully")
            # Clear the entry
            self.email_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting user: {str(e)}")

    # Function to go back to the main menu
    def back(self):
        self.root.destroy()

# Create the main window
root = tk.Tk()
root.title("Delete User")
DeleteUserGUI(root)
root.mainloop()