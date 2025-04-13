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
   ```

2. **Install Python and Requirements:**
   - Make sure you have python installed with the `˅3.9` version as I'm not sure it would work on newer versions
   - Install CMAKE from their website and add it to the environment variables for the dlib library to work
   - Run the following command:
     
   ```bash
   pip install -r requirements.txt
   ```

   - If you find any missing libraries when executing one of the scripts please do install them until i add all of them

3. **Set up Firebase:**
   - Create a Firebase project on the [Firebase Console](https://console.firebase.google.com/).
   - Enable Firebase Authentication and Firebase Realtime Database.
   - Download the `firebase-adminsdk` credentials JSON file and add it to the credentials folder as `AdminCredentials.json`.
   - Add a new web app to the Firebase project and copy the credentials and add it to the credentials folder as `UserCredentials.json`.
  
4. **Acquire the face detection related models:**
   - Create a `Models` folder in your main directory
   - Download the YuNet model `face_detection_yunet_2023mar.onnx` and add it to the `Models` folder
   - Download the dlib `Shape_predictor_68_face_landmarks.dat` and add it to the `Models` folder
  
5. **Separate into the ADMIN side and the LECTURER side**
   - When actually deploying, make sure the `LecturerSideScripts, LecturerUtilities, GeneralUtilities` and only the `UserCredentials` of the `Credentials` folder and all the models in the `Models` folder are on the lecturer side machine.
   - Put the `AdminSideScripts, AdminUtilities, GeneralUtilities` and both the `UserCredentials, AdminCredentials` in a `credentials` folder and all the models as well in a `Models` folder.
     
6. **Run the application:**

  ### For the Admin SIDE:
   ```bash
   python AddClassGUI.py
   ```

  After adding classes, add the students and lecturers through:

  ```bash
  python SignUpGUI.py
  ```

  And if you wish to delete a user run:
  ```bash
  python DeleteUserGUI.py
  ```

  ### For the Lecturer SIDE:

  Sign in as a lecturer and control student attendance:
  
  ```bash
  python LecturerGUI.py
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

## Credits
This project was inspired by and takes some code from the [Intelligent Face Recognition Attendance System](https://github.com/turhancan97/Intelligent-Face-Recognition-Attendance-System) by turhancan97, which is licensed under the MIT License.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

