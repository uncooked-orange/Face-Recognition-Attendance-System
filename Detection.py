import cv2
import numpy as np
import dlib
import json
from deepface import DeepFace
from scipy.spatial.distance import cosine
from typing import List, Dict, Optional, Tuple

class FaceRecognitionSystem:
    def __init__(self, 
                 model_path: str = "Models/best.onnx", # Open Neural Network Exchange (ONNX) model
                 landmarks_path: str = "Models/shape_predictor_68_face_landmarks.dat"):
        """
        Initialize the Face Recognition System
        
        Parameters
        ----------
        model_path : str
            Path to the YOLO ONNX model file
        landmarks_path : str
            Path to the dlib facial landmarks predictor file
        """
        # Initialize YOLO model
        self.model_path = model_path
        self.net = cv2.dnn.readNetFromONNX(model_path)
        
        # Initialize landmark detection using dlib 68 landmarks predictor model
        self.landmark_predictor = dlib.shape_predictor(landmarks_path)
        
        # Database for face recognition
        self.face_database: Dict[str, List[float]] = {}
        
        # YOLO parameters
        self.input_width = 640
        self.input_height = 640
        self.score_threshold = 0.5
        self.nms_threshold = 0.45

    def detect_faces(self, img: np.ndarray, scale_factor: float = 1.0) -> np.ndarray:
        """
        Detect faces in an image using YOLO
        
        Parameters
        ----------
        img : numpy.ndarray
            Input image for face detection
        scale_factor : float, optional
            Scale factor to adjust image size, by default 1.0
        
        Returns
        -------
        numpy.ndarray
            Detected faces with coordinates [x, y, width, height]
        """
        # Get original image dimensions
        height, width = img.shape[:2]
        
        # Prepare image for YOLO
        blob = cv2.dnn.blobFromImage(
            img, 
            1/255.0, 
            (self.input_width, self.input_height), 
            swapRB=True, 
            crop=False
        )
        
        # Set input and get output
        self.net.setInput(blob)
        outputs = self.net.forward()[0]
        
        # Process detections
        boxes = []
        confidences = []
        
        for detection in outputs:
            confidence = detection[4]
            
            if confidence > self.score_threshold:
                # YOLO outputs normalized coordinates
                x = detection[0]
                y = detection[1]
                w = detection[2]
                h = detection[3]
                
                # Convert normalized coordinates to pixel coordinates
                x_pixel = int((x - w/2) * width)
                y_pixel = int((y - h/2) * height)
                w_pixel = int(w * width)
                h_pixel = int(h * height)
                
                # Ensure coordinates are within image bounds
                x_pixel = max(0, x_pixel)
                y_pixel = max(0, y_pixel)
                w_pixel = min(w_pixel, width - x_pixel)
                h_pixel = min(h_pixel, height - y_pixel)
                
                boxes.append([x_pixel, y_pixel, w_pixel, h_pixel])
                confidences.append(float(confidence))
        
        # Convert to numpy array
        if boxes:
            # Properly format boxes for NMSBoxes
            boxes_for_nms = [[box[0], box[1], box[0] + box[2], box[1] + box[3]] for box in boxes]
            
            # Apply Non-Maximum Suppression
            indices = cv2.dnn.NMSBoxes(
                boxes_for_nms,
                confidences,
                self.score_threshold,
                self.nms_threshold
            ).flatten()
            
            # Convert selected boxes back to [x, y, w, h] format
            selected_faces = np.array([boxes[i] for i in indices])
            return selected_faces
        
        return np.array([])

    # Rest of the methods remain the same
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

    def align_face(self, img: np.ndarray, face: List[int], scale_factor: float = 0.27) -> np.ndarray:
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
            Distance threshold for a match, by default 0.70
        
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