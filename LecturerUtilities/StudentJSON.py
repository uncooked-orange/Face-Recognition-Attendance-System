import json
import logging
import os
import stat

class AttendanceManager:
    def __init__(self, database, lecturer_id, lecturer_token=None, local_data_path=None):
        """
        Initialize the Attendance Manager for a specific lecturer
        
        Args:
            database (firebase_admin.db.child): Firebase database reference
            lecturer_id (str): Unique identifier for the lecturer
            local_data_path (str, optional): Directory path for storing local student data
        """
        try:
            self.lecturer_token = lecturer_token
            self.database = database
            self.lecturer_id = lecturer_id
            self.local_students = None
            self.lecturer_info = None
            
            # Set up local data directory if provided
            if local_data_path:
                # Ensure the directory exists
                os.makedirs(local_data_path, exist_ok=True)
                self.local_data_path = local_data_path
            else:
                # Use a default directory in the current working directory
                default_path = os.path.join(os.getcwd(), "attendance_data")
                os.makedirs(default_path, exist_ok=True)
                self.local_data_path = default_path

            # Set directory permissions (read, write, and execute for owner and group)
            os.chmod(self.local_data_path, stat.S_IRWXU | stat.S_IRWXG)
        
        except Exception as e:
            logging.error(f"Attendance Manager initialization failed: {e}")
            raise

    def fetch_students(self):
        """
        Fetch and store students relevant to the lecturer's classes locally

        Organizes students in a nested dictionary structure:
        {
            study: {
                branch: {
                    student_id: {
                        name: student_name,
                        attendance: student_attendance,
                        embedding: [0:(embedding 0), 1:(embedding 1), ...],
                        classes : {
                            class_name: attendance
                        }
                    }
                }
            }
        }

        Returns:
            dict: Structured student information for lecturer's classes
        """
        try:
            lecturer_data = self.database.child(f"Lecturers/{self.lecturer_id}").get(token=self.lecturer_token).val()
            if not lecturer_data:
                raise ValueError(f"No lecturer found with ID {self.lecturer_id}")

            self.lecturer_info = {
                "id": self.lecturer_id,
                "name": lecturer_data.get("Name", "Unknown"),
                "classes": list(lecturer_data.get("classes", {}).keys())
            }

            lecturer_classes = self.lecturer_info["classes"]
            if not lecturer_classes:
                raise ValueError(f"No classes found for lecturer {self.lecturer_id}")

            all_students = self.database.child("Students").get(token=self.lecturer_token).val()

            students = {}
            for student_id, student_data in all_students.items():
                # Check if student has any of the lecturer's classes
                student_classes = student_data.get("classes", {})
                relevant_classes = {class_name: attendance 
                                 for class_name, attendance in student_classes.items() 
                                 if class_name in lecturer_classes}
                
                # Skip student if they're not in any of the lecturer's classes
                if not relevant_classes:
                    continue

                study_type = student_data.get("study", "Unknown")
                branch = student_data.get("branch", "Unknown")
                
                if study_type not in students:
                    students[study_type] = {}
                if branch not in students[study_type]:
                    students[study_type][branch] = {}

                students[study_type][branch][student_id] = {
                    "name": student_data.get("Name", ""),
                    "classes": relevant_classes,
                    "embedding": student_data.get("embedding", [])
                }

            self.local_students = {
                "lecturer_info": self.lecturer_info,
                "students": students
            }

            return self.local_students

        except Exception as e:
            logging.error(f"Failed to fetch students: {e}")
            return None


    def save_students_locally(self, filename="Students.json"):
        """
        Save fetched students to a local JSON file
        
        Args:
            filename (str, optional): Name of the file to save students data
        """
        if self.local_students is None:
            raise ValueError("No students fetched. Call fetch_students() first.")
        
        try:
            # Use the full path from local_data_path
            full_filepath = os.path.join(self.local_data_path, filename)
            
            # Save data to the file
            with open(full_filepath, "w") as f:
                json.dump(self.local_students, f, indent=4)

            # Set file permissions (read and write for owner and group)
            os.chmod(full_filepath, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP)

            logging.info(f"Students saved to {full_filepath}")
        
        except Exception as e:
            logging.error(f"Failed to save students locally: {e}")

    def load_local_students(self, filename="Students.json"):
        """
        Load students from a local JSON file
        
        Args:
            filename (str, optional): Name of the file to load students from
        
        Returns:
            dict: Loaded students data
        """
        try:
            # Use the full path from local_data_path
            full_filepath = os.path.join(self.local_data_path, filename)
            
            # Load data from the file
            with open(full_filepath, "r") as f:
                self.local_students = json.load(f)

            # Ensure file permissions are appropriate (read and write for owner and group)
            os.chmod(full_filepath, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP)

            # Update lecturer_info as an instance attribute
            self.lecturer_info = self.local_students.get("lecturer_info")
            
            return self.local_students
        
        except FileNotFoundError:
            logging.error(f"File {filename} not found in {self.local_data_path}")
            return None
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON in {filename}")
            return None
        except Exception as e:
            logging.error(f"Failed to load local students: {e}")
            return None
        
    def upload_local_students(self):
        """
        Upload local students data to Firebase

        This method updates the attendance for students in a specific class, study type, and branch.
        It navigates through the nested dictionary structure of local students data.

        Returns:
            bool: Whether the upload was successful
        """
        if self.local_students is None:
            raise ValueError("No local students data to upload")

        try:
            students = self.local_students["students"]
            for study_type, branches in students.items():
                for branch, branch_students in branches.items():
                    for student_id, student_info in branch_students.items():
                        for class_name, attendance in student_info["classes"].items():
                            # Update each class attendance separately
                            student_ref = self.database.child(f"Students/{student_id}/classes")
                            student_ref.update({
                                class_name: attendance
                            }, token=self.lecturer_token)

            logging.info("Successfully uploaded local students data")
            return True

        except Exception as e:
            logging.error(f"Failed to upload students data: {e}")
            return False