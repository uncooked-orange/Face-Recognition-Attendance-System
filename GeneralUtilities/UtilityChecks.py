import re

# check if class exists
def check_class_exists(class_name,database):
    ref = database.reference('/Classes')
    classes = ref.get()
    if classes:
        if class_name in classes:
            return True
    return False

# check if user exists
def check_user_exists(email,auth):
    try:
        user = auth.get_user_by_email(email)
        return True
    except:
        return False



# check class name is valid
def check_class_name_valid(class_name):
    pattern = r'^[A-Za-z0-9\s]+$'
    return bool(re.match(pattern, class_name))

# check if branch is valid
def check_branch_valid(branch):
    # Valid branches
    valid_branches = ['IT', 'NE']

    # Check if branch exists
    if not branch:
        raise ValueError("Branch is required")

    # If branch is a string, validate it
    if isinstance(branch, str):
        if branch not in valid_branches:
            raise ValueError(f"Branch '{branch}' is invalid. Must be one of {valid_branches}.")
        return True

    # If branch is a dictionary, validate keys
    if isinstance(branch, dict):
        if not all(s in valid_branches for s in branch.keys()):
            raise ValueError(f"One or more branches in the dictionary are invalid. Must be one of {valid_branches}.")
        return True

    # If branch is neither a string nor a dictionary, raise an error
    raise ValueError("Branch must be a string or a dictionary.")


# check if semester is valid
def check_semester_valid(semester):
    # Check if semester exists
    if not semester:
        raise ValueError("Semester is required")
    # Check if all elements in the list are either '1' or '2'
    valid_semesters = ['1', '2']
    return all(s in valid_semesters for s in semester.keys())


# check if name is valid
def check_name_valid(name):
    return True

# check if email is valid
def check_email_valid(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    try:
        if not email.strip():
            raise ValueError("Email is required")
        if not re.match(pattern, email):
            raise ValueError("Email is invalid")
        return True
    except ValueError:
        return False

# check if password is valid
def check_password_valid(password):
    try:
        if not password or len(password) < 6:
            raise ValueError("Password is required")
        return True
    except ValueError:
        return False

# check password and confirm password match
def check_password_match(password, confirm_password):
    try:
        if password != confirm_password:
            raise ValueError("Passwords do not match")
        return True
    except ValueError:
        return False

# check if week is valid
def check_week_valid(week):
    try:
        if not week in range(1, 14):
            raise ValueError("Week is invalid")
        return True
    except ValueError:
        return False

# check if attendance is valid (array of 13 boolean values)
def check_attendance_valid(attendance):
    try:
        if len(attendance) != 13 or not all(isinstance(x, int) for x in attendance):
            raise ValueError("Attendance is invalid")
        return True
    except ValueError:
        return False

# check if role is valid
def check_role_valid(role):
    try:
        if role not in ['Lecturer', 'Student']:
            raise ValueError("Role is invalid")
        return True
    except ValueError:
        return False

# check if stage is valid
def check_stage_valid(stage):
    try:
        if stage not in ['1', '2', '3', '4']:
            raise ValueError("Stage is invalid")
        return True
    except ValueError:
        return False

# check if study is valid
def check_study_valid(study):
    try:
        if study not in ['Morning', 'Evening']:
            raise ValueError("Study is invalid")
        return True
    except ValueError:
        return False

# check student info valid
def check_student_info(email, password, confirm_password, name, stage, branch, study):
    if not check_email_valid(email):
        raise ValueError("Invalid email address.")
    if not check_password_valid(password):
        raise ValueError("Invalid password. Password must be at least 6 characters long.")
    if not check_password_match(password, confirm_password):
        raise ValueError("Passwords do not match.")
    if not check_name_valid(name):
        raise ValueError("Invalid name.")
    if not check_branch_valid(branch):
        raise ValueError("Invalid branch.")
    if not check_study_valid(study):
        raise ValueError("Invalid study.")
    if not check_stage_valid(stage):
        raise ValueError("Invalid stage.")
    return True
