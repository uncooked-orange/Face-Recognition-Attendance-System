from UtilityChecks import check_email_valid, check_password_valid, check_user_exists, check_stage_valid, check_study_valid, check_class_exists, check_branch_valid, check_name_valid

# get all classes with same branch and stage as student and add them to student
def add_classes_to_student(stage, branch, Database):
    student_classes = {}
    try:
        classes = Database.reference("/").child('Classes').get()
        if classes:
            for key, val in classes.items():
                # Check for necessary keys in each class entry
                if val["stage"] == stage and (val["branch"] == branch or branch in val["branch"]):
                    class_name = key
                    if class_name:  # Check if class_name exists
                        student_classes[class_name] = [0] * 13
    except Exception as e:
        print(f"Error retrieving classes: {e}")
    
    return student_classes

# function for signing up a Lecturer
def sign_up_lecturer(Email, Pass, classes, Name, Database, Auth):
    try:
        # check if email, password, role, name are valid
        if not check_email_valid(Email):
            print("Invalid Email")
            return

        if not check_password_valid(Pass):
            print("Invalid Password")
            return

        if not check_name_valid(Name):
            print("Invalid Name")
            return
        
        # check if classes exist
        for class_name in classes:
            if not check_class_exists(class_name, Database):
                print(f"Class {class_name} does not exist")
                return

        # check if user exists
        if check_user_exists(Email,Auth):
            print("User already exists")
            return

        # create user
        user = Auth.create_user(
            email=Email,
            password=Pass
            )

        # add custom claims
        Auth.set_custom_user_claims(user.uid, {'role': 'Lecturer'})
        print("Successfully created new user: {0}".format(user.uid))

        # Turn classes into a dictionary for easier access
        classes = {class_name: True for class_name in classes}
        # add Lecturer to database
        Database.reference('/').child('Lecturers').child(user.uid).set({
            'Name': Name,
            'email': Email, 
            'classes': classes
            })

    except Exception as e:
        raise ValueError(f"Error creating new user: {e}")

# function for adding a Student
def sign_up_student(Email, Pass, Name, Study, Stage, branch, embedding, Database, Auth):
    try:
        # check if email, password,  name are valid
        if not check_email_valid(Email):
            print("Invalid Email")
            exit(0)

        if not check_password_valid(Pass):
            print("Invalid Password")
            exit(0)

        if not check_name_valid(Name):
            print("Invalid Name")
            exit(0)

        # check if stage, study are valid
        if not check_stage_valid(Stage):
            print("Invalid Stage")
            return

        if not check_study_valid(Study):
            print("Invalid Study")
            return
        
        # add classes to student
        classes = add_classes_to_student(Stage, branch, Database=Database)

        # check if user exists
        if check_user_exists(Email,Auth):
            print("User already exists")
            exit(0)

        # create user
        user = Auth.create_user(
            email=Email,
            password=Pass
            )

        # add custom claims
        Auth.set_custom_user_claims(user.uid, {
            'role': 'Student', 
            })
        
        print("Successfully created new user: {0}".format(user.uid))

        # add Student to database
        Database.reference('/').child('Students').child(user.uid).set({
            'Name': Name, 
            'email': Email, 
            'classes': classes, 
            'study': Study, 
            'stage': Stage, 
            'branch': branch,
            'embedding': embedding
            })


    except Exception as e:
        raise ValueError(f"Error creating new user: {e}")
