"""
# Attendance System

A Python-based Attendance System with a graphical user interface (GUI) built using Tkinter. The system integrates with Firebase for online functionality and supports offline capabilities. The system allows lecturers to take attendance manually or automatically using a face detection system.

## Features

- **User Authentication** (Firebase authentication for secure access)
- **Subject, Lecturer, and Student Management** (Add and manage subjects, lecturers, and students)
- **Attendance Tracking** (Mark attendance manually or using a face detection system)
- **Offline Functionality** (Lecturers can take attendance offline, with data synced once online)
- **Face Detection Integration** (Automatically mark attendance using a face detection system)
- **Real-time Sync with Firebase** (Store attendance data securely in Firebase)
- **Tkinter GUI** (Intuitive interface for lecturers to manage attendance and subjects)

## Technologies Used

- **Python** (Main programming language)
- **Tkinter** (GUI library for creating the application interface)
- **Firebase** (Realtime database for storing attendance and user data)
- **Face Detection** (Used for automatic attendance marking)
- **OpenCV** (For face detection)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/attendance-system.git
   cd attendance-system

2. **Install Python and Requirements:**
   - Make sure you have python installed with at least the `^3.8.9` version
   - Run the command
   ```bash
   pip install -r requirements.txt
   ```
   - Make Sure to install CMAKE for the dlib to work aswell

3. **Set up Firebase:**
   - Create a Firebase project on the [Firebase Console](https://console.firebase.google.com/).
   - Enable Firebase Authentication and Firebase Realtime Database.
   - Download the `firebase-adminsdk` credentials JSON file and add it to the credentials folder As `AdminCredentials.json`.
   - Add a new web app to the firebase project and copy the credentials and add it to the credentials folder As `UserCredentials.json`.
  
4. **Acquire the face detection related models:**
   - Download the yunet model `face_detection_yunet_2023mar.onnx` and add it to a `Models` folder
   - Add the dlib `Shape_predictor_68_face_landmarks.dat` and add it to the `Models` folder
  
4. **Separate into the ADMIN side and the LECTURER side**
   - When actually deploying, make sure the `LecturerSideScripts, LecturerUtilites, GeneralUtlitiles` and only the `UserCredentials` of the `Credentials` folder         and all the models in the `Models` folder are on the lecturer side machine
   - Put the `AdminSideScripts, AdminUtilities, GeneralUtilites` and Both the `UserCredentials, AdminCredentials` and all the models
     
5. **Run the application:**

  ### For the Admin SIDE:-
   ```bash
   python AddClassGUI.py
   ```

  after adding classes add the students and lecturers through:

  ```bash
  python SignUpGUI.py
  ```

  ### For the Lecturers SIDE:-

  sign in as a lecturer and control the student attendance
  
  ```bash
  python SignInGUI.py
  ```

## Features Walkthrough

### Authentication
- **Login/Signup:** Lecturers can authenticate using Firebase credentials.
- **User Roles:** Admins can add/remove lecturers, students, and subjects.

### Subject, Lecturer, and Student Management
- **Add Subjects:** Admins can add new subjects to the system.
- **Manage Lecturers:** Admins can add/remove lecturers.
- **Manage Students:** Admins can add/remove students to/from subjects.

### Attendance Tracking
- **Manual Attendance:** Lecturers can mark attendance by selecting students.
- **Face Detection:** The system can automatically detect students using facial recognition and mark attendance.

### Offline Mode
- **Local Storage:** The system can store attendance data locally when offline and sync it with Firebase once internet access is available.
