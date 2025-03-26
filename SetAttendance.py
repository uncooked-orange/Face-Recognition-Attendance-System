import pyrebase as pb
from UtilityChecks import check_email_valid, check_attendance_valid

firebaseConfig = {
  'apiKey': "AIzaSyBvqENPduLshnXGgmOooc0eTvHZMtU-NzI",
  'authDomain': "face-recognition-attenda-9476f.firebaseapp.com",
  'databaseURL': "https://face-recognition-attenda-9476f-default-rtdb.asia-southeast1.firebasedatabase.app",
  'projectId': "face-recognition-attenda-9476f",
  'storageBucket': "face-recognition-attenda-9476f.appspot.com",
  'messagingSenderId': "439802013226",
  'appId': "1:439802013226:web:c46ee8f3581489662ec553"
}

# Initialize Firebase
firebase = pb.initialize_app(firebaseConfig)
database = firebase.database()
auth = firebase.auth()


# get student ID function from email
def get_student_id(Email, Token):
    try:
        # check if email is valid
        if not check_email_valid(Email):
            print("Invalid Email")
            exit(0)

        # read from the database using the token
        data = database.child("Students").get(token=Token)
        students = data.val()
        for key, val in students.items():
            if val['email'] == Email:
                return key
        print("Student not found")
        exit(0)
    except Exception as e:
        print(f"Error getting student ID: {str(e)}")

# set attendance function
def set_attendance(StudentID, Class, LecturerToken, attendance):
    try:
        if not check_attendance_valid(attendance):
            print("Invalid Attendance")
            exit(0)

        # write to the database
        database.child("Students").child(StudentID).child("classes").child(Class).set(attendance, token=LecturerToken)
        print(f"Successfully set attendance for {StudentID} in {Class} : {attendance}")

    except Exception as e:
        print(f"Error setting attendance: {str(e)}")

# Get user input
#Email = input("Enter your email: \t")
#Pass = input("Enter your password: \t")
#Week = int(input("Enter the week number: \t"))
#StudentEmail = input("Enter the student's email: \t")
#Subject = input("Enter the subject: \t")
#
## Sign in user
#user = auth.sign_in_with_email_and_password(Email, Pass)
#
## Set attendance
#set_attendance(StudentEmail, Subject, Week, user['idToken'])