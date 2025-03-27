import cv2
import numpy as np
import dlib
import json
from deepface import DeepFace
from scipy.spatial.distance import cosine
from typing import List, Dict, Optional, Tuple

class FaceRecognitionSystem:
    def __init__(self, 
                 model_path: str = "Models/face_detection_yunet_2023mar.onnx", 
                 landmarks_path: str = "Models/shape_predictor_68_face_landmarks.dat"):
        """
        Initialize the Face Recognition System
        
        Parameters
        ----------
        model_path : str
            Path to the YuNet ONNX model file
        landmarks_path : str
            Path to the dlib facial landmarks predictor file
        """
        # Initialize face detection using YuNet
        self.model_path = model_path
        self.face_detector = cv2.FaceDetectorYN_create(model_path, "", (640, 480))
        
        # Initialize landmark detection using dlib 68 landmarks predictor model
        self.landmark_predictor = dlib.shape_predictor(landmarks_path)
        
        # Database for face recognition
        self.face_database: Dict[str, List[float]] = {}

    def load_students_from_json(self, json_path: str, class_name: str) -> None:
        """
        Load student data from AttendanceManager JSON file and update face database
        
        Parameters
        ----------
        json_path : str
            Path to the JSON file containing student data
        class_name : str
            Name of the class to filter students by
        """
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)

            students = data.get('students', {})
            for study_type in students.values():
                for branch in study_type.values():
                    for student_id, student_info in branch.items():
                        # Check if student is enrolled in the specified class
                        if class_name in student_info.get('classes', {}):
                            embedding = student_info.get('embedding')
                            if embedding and isinstance(embedding, list):
                                self.face_database[student_id] = embedding
                            
        except Exception as e:
            print(f"Error loading student data: {e}")

    def detect_faces(self, img: np.ndarray, scale_factor: float = 1.0) -> np.ndarray:
        """
        Detect faces in an image using YuNet
        
        Parameters
        ----------
        img : numpy.ndarray
            Input image for face detection
        scale_factor : float, optional
            Scale factor to adjust image size, by default 1.0
        
        Returns
        -------
        numpy.ndarray
            Detected faces with coordinates
        """
        # Get original image dimensions
        height, width = img.shape[:2]
        
        # Calculate dynamic input size
        input_width = int(width * scale_factor)
        input_height = int(height * scale_factor)
        
        # Set input size and resize image
        self.face_detector.setInputSize((input_width, input_height))
        resized_img = cv2.resize(img, (input_width, input_height), interpolation=cv2.INTER_AREA)

        # Detect faces
        _, results = self.face_detector.detect(resized_img)

        # If no faces detected, return empty array
        if results is None or len(results) == 0:
            return np.array([])

        # Scale back the detected faces to original image coordinates
        faces = results[:, :4].astype(np.int32)
        
        # Scale coordinates back to original image size
        scale_x = width / input_width
        scale_y = height / input_height
        
        scaled_faces = faces.copy()
        scaled_faces[:, 0] = (faces[:, 0] * scale_x).astype(np.int32)  # x
        scaled_faces[:, 1] = (faces[:, 1] * scale_y).astype(np.int32)  # y
        scaled_faces[:, 2] = (faces[:, 2] * scale_x).astype(np.int32)  # width
        scaled_faces[:, 3] = (faces[:, 3] * scale_y).astype(np.int32)  # height
        
        return scaled_faces

    def align_face(self, img: np.ndarray, face: List[int],scale_factor: float = 0.27) -> np.ndarray:
        """
        Align a detected face based on eye positions
        
        Parameters
        ----------
        img : numpy.ndarray
            Input image containing the face
        face : List[int]
            Face bounding box coordinates [x, y, width, height]
        
        Returns
        -------
        numpy.ndarray
            Aligned face image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Create dlib rectangle
        rect = dlib.rectangle(
            int(face[0]), int(face[1]), 
            int(face[0] + face[2]), int(face[1] + face[3])
        )

        # Detect facial landmarks
        shape = self.landmark_predictor(gray, rect)
        shape = np.array(
            [(shape.part(j).x, shape.part(j).y) for j in range(shape.num_parts)]
        )

        # Specify aligned face size
        desired_face_width, desired_face_height = 256, 256

        # Eye landmark indexes
        left_eye_landmarks = [36, 37, 38, 39, 40, 41]
        right_eye_landmarks = [42, 43, 44, 45, 46, 47]

        # Calculate eye centers
        left_eye_center = np.mean(shape[left_eye_landmarks], axis=0).astype(int)
        right_eye_center = np.mean(shape[right_eye_landmarks], axis=0).astype(int)

        # Calculate rotation angle
        dY = right_eye_center[1] - left_eye_center[1]
        dX = right_eye_center[0] - left_eye_center[0]
        angle = np.degrees(np.arctan2(dY, dX))

        # Calculate scale
        dist = np.sqrt((dX**2) + (dY**2))
        desired_dist = desired_face_width * scale_factor
        scale = desired_dist / dist

        # Calculate eye center
        eyes_center = (
            int((left_eye_center[0] + right_eye_center[0]) // 2),
            int((left_eye_center[1] + right_eye_center[1]) // 2),
        )

        # Get rotation matrix
        M = cv2.getRotationMatrix2D(eyes_center, angle, scale)

        # Update translation
        tX = desired_face_width * 0.5
        tY = desired_face_height * 0.3
        M[0, 2] += tX - eyes_center[0]
        M[1, 2] += tY - eyes_center[1]

        # Apply transformation
        output = cv2.warpAffine(
            img, M, (desired_face_width, desired_face_height), 
            flags=cv2.INTER_CUBIC
        )

        return output

    def extract_features(self, face: np.ndarray) -> List[float]:
        """
        Extract facial features using DeepFace
        
        Parameters
        ----------
        face : numpy.ndarray
            Aligned face image
        
        Returns
        -------
        List[float]
            Face embedding
        """
        # Convert to RGB
        face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)

        # Extract embedding
        embedding = DeepFace.represent(
            face_rgb, 
            model_name="Facenet", 
            enforce_detection=False
        )

        return embedding[0]['embedding']

    def add_to_database(self, ID: str, embedding: List[float]) -> None:
        """
        Add a face to the recognition database
        
        Parameters
        ----------
        ID : str
            ID or identifier for the face
        embedding : List[float]
            Face embedding to store
        """
        self.face_database[ID] = embedding

    def match_face(self, embedding: List[float], threshold: float = 0.70) -> Optional[str]:
        """
        Match a face embedding against the database
        
        Parameters
        ----------
        embedding : List[float]
            Face embedding to match
        threshold : float, optional
            Distance threshold for a match, by default 0.50
        
        Returns
        -------
        Optional[str]
            ID of matched face or None
        """
        min_distance = float('inf')
        match = None

        # Compare against database
        for ID, db_embedding in self.face_database.items():
            distance = cosine(embedding, db_embedding)
            
            if distance < min_distance:
                min_distance = distance
                match = ID

        # Return match if below threshold
        return match if min_distance < threshold else None

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List[str]]:
        """
        Process a full frame for face detection and recognition
        
        Parameters
        ----------
        frame : numpy.ndarray
            Input video frame
        
        Returns
        -------
        Tuple[numpy.ndarray, List[str]]
            Processed frame and list of recognized faces
        """
        # Detect faces
        faces = self.detect_faces(frame)
        
        # List to store recognized names
        recognized_names = []
        
        # Process each detected face
        for face in faces:
            try:
                # Align the face
                aligned_face = self.align_face(frame, face)
                
                # Extract features
                embedding = self.extract_features(aligned_face)
                
                # Match face
                match = self.match_face(embedding)
                
                if match:
                    recognized_names.append(match)
                    
                    # Draw bounding box and name
                    x, y, w, h = face
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            except Exception as e:
                print(f"Error processing face: {e}")
        
        return frame, recognized_names
