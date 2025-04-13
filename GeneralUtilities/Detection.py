import cv2
import numpy as np
import dlib
import json
from deepface import DeepFace
from scipy.spatial.distance import cosine
from typing import List, Dict, Optional, Tuple, Union
import time
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import threading

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
        self.face_database: Dict[str, List[List[float]]] = {}
        
        # Temporal consistency tracking
        self.recent_matches = {}  # ID -> count of recent matches
        self.frame_history = []   # Store last N matches
        self.consistency_threshold = 3  # How many frames to require for confirmation
        self.last_detection_time = {}  # Track when each ID was last detected
        
        # Quality assessment parameters
        self.min_face_size = 100
        self.min_sharpness = 10
        self.min_brightness = 20
        self.max_brightness = 300
        
        # Matching parameters
        self.match_threshold = 0.5  # Stricter threshold for matching
        
        # Store embedding dimensions to verify consistency
        self.embedding_dim = None

    def load_students_from_json(self, json_path: str, class_name: str) -> None:
        """
        Load student data from AttendanceManager JSON file and update face database
        """
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)

            # Get students from the structure created by AttendanceManager
            all_students = data.get('students', {})

            # Process each study type, branch, and student
            for study_type, branches in all_students.items():
                for branch, students in branches.items():
                    for student_id, student_info in students.items():
                        # Check if student is enrolled in the specified class
                        if class_name in student_info.get('classes', {}):
                            # Try to get multiple embeddings first (if you update Firebase to store multiple)
                            embeddings = student_info.get('embedding', [])

                            # Store only if we have valid embeddings
                            if embeddings and all(isinstance(emb, list) for emb in embeddings):
                                # Check and store embedding dimension if not set
                                if self.embedding_dim is None and embeddings and len(embeddings) > 0:
                                    self.embedding_dim = len(embeddings[0])
                                    print(f"Setting embedding dimension to: {self.embedding_dim}")
                                
                                # Validate embedding dimensions before adding to database
                                valid_embeddings = []
                                for emb in embeddings:
                                    if len(emb) == self.embedding_dim:
                                        valid_embeddings.append(emb)
                                    else:
                                        print(f"Warning: Skipping embedding with incorrect dimension for student {student_id}. Expected {self.embedding_dim}, got {len(emb)}")
                                
                                if valid_embeddings:
                                    self.face_database[student_id] = valid_embeddings
                                    print(f"Added student {student_id} with {len(valid_embeddings)} valid embeddings")

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
        x, y, w, h = face
        rect = dlib.rectangle(
            int(x), int(y), 
            int(x + w), int(y + h)
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

    def assess_face_quality(self, face_img: np.ndarray) -> bool:
        """
        Assess if a face is high quality enough for recognition
        
        Parameters
        ----------
        face_img : numpy.ndarray
            Aligned face image
            
        Returns
        -------
        bool
            True if face passes quality checks, False otherwise
        """
        try:
            # Check image sharpness
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        except Exception as e:
            print(f"Error calculating sharpness: {e}")
            return False
        
        try:
            # Check illumination
            brightness = np.mean(gray)
        except Exception as e:
            print(f"Error calculating brightness: {e}")
            return False
        
        try:
            # Check face size
            height, width = face_img.shape[:2]
            face_size = min(height, width)
        except Exception as e:
            print(f"Error calculating face size: {e}")
            return False
        
        try:
            # Check sharpness
            if laplacian_var <= self.min_sharpness:
                print(f"Sharpness check failed: {laplacian_var} <= {self.min_sharpness}")
                return False

            # Check brightness
            if brightness <= self.min_brightness:
                print(f"Brightness too low: {brightness} <= {self.min_brightness}")
                return False
            if brightness >= self.max_brightness:
                print(f"Brightness too high: {brightness} >= {self.max_brightness}")
                return False

            # Check face size
            if face_size <= self.min_face_size:
                print(f"Face size too small: {face_size} <= {self.min_face_size}")
                return False

            # If all checks pass
            return True
        except Exception as e:
            print(f"Error evaluating quality checks: {e}")
            return False

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
        # Pre-process the image
        face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        
        # Normalize the image
        face_rgb = face_rgb.astype(np.float32) / 255.0
        face_rgb = (face_rgb * 255).astype(np.uint8)  # Convert back to uint8 for DeepFace
        
        # Extract embedding
        embedding = DeepFace.represent(
            face_rgb, 
            model_name="Facenet", 
            enforce_detection=False
        )
        
        # Store embedding dimension if not already set
        if self.embedding_dim is None:
            self.embedding_dim = len(embedding[0]['embedding'])
            print(f"Setting embedding dimension from extraction: {self.embedding_dim}")
            
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
        # Check dimension consistency
        if self.embedding_dim is None:
            self.embedding_dim = len(embedding)
            print(f"Setting embedding dimension: {self.embedding_dim}")
        elif len(embedding) != self.embedding_dim:
            print(f"Warning: Embedding dimension mismatch. Expected {self.embedding_dim}, got {len(embedding)}. Skipping.")
            return
            
        if ID in self.face_database:
            # Check if we already have embeddings for this ID
            if isinstance(self.face_database[ID][0], list):
                # Limit to 5 embeddings per person
                if len(self.face_database[ID]) < 5:
                    self.face_database[ID].append(embedding)
            else:
                # Convert to list of embeddings
                self.face_database[ID] = [self.face_database[ID], embedding]
        else:
            # Create new entry with embedding in a list
            self.face_database[ID] = [embedding]

    def match_face(self, embedding: List[float], threshold: float = None) -> Optional[str]:
        """
        Match a face embedding against the database by calculating the average cosine similarity 
        across all embeddings for each person. Returns the ID of the best match or None if no 
        match under threshold.
        """
        if threshold is None:
            threshold = self.match_threshold
    
        if self.embedding_dim is None:
            self.embedding_dim = len(embedding)
            print(f"Setting embedding dimension: {self.embedding_dim}")
        elif len(embedding) != self.embedding_dim:
            print(f"Warning: Input embedding dimension {len(embedding)} doesn't match expected {self.embedding_dim}")
            return None
    
        best_avg_distance = float('inf')
        best_match_id = None
        embedding_array = np.array(embedding).flatten()
    
        for ID, embeddings in self.face_database.items():
            try:
                if not embeddings:
                    continue
                
                valid_embeddings = []
                if isinstance(embeddings[0], list):  # Multiple embeddings
                    for emb in embeddings:
                        if not emb or not isinstance(emb, list):
                            continue
                        if len(emb) != self.embedding_dim:
                            continue
                        emb_array = np.array(emb).flatten()
                        valid_embeddings.append(emb_array)
                else:  # Single embedding
                    if len(embeddings) != self.embedding_dim:
                        continue
                    valid_embeddings.append(np.array(embeddings).flatten())
    
                # Skip if no valid embeddings
                if not valid_embeddings:
                    continue
                    
                # Calculate average distance across all embeddings for this ID
                total_distance = 0
                for db_embedding in valid_embeddings:
                    total_distance += cosine(embedding_array, db_embedding)
                
                avg_distance = total_distance / len(valid_embeddings)

                print(f"ID: {ID}, Avg Distance: {avg_distance:.4f}")
                
                # Update best match if this average is better
                if avg_distance < best_avg_distance:
                    best_avg_distance = avg_distance
                    best_match_id = ID
                    
            except Exception as e:
                print(f"Error processing ID {ID}: {e}")
                continue
            
        if best_avg_distance < threshold:
            print(f"Match found: {best_match_id} with average distance {best_avg_distance:.4f}")
            return best_match_id
    
        return None

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List[str]]:
        """
        Process a single image frame for face detection and recognition (no consistency tracking).
        """
        display_frame = frame.copy()
        faces = self.detect_faces(frame)
        recognized_names = []

        for face in faces:
            try:
                # Align the face
                aligned_face = self.align_face(frame, face)

                # Check quality
                if not self.assess_face_quality(aligned_face):
                    print("Face quality check failed.")
                    continue

                # Extract features
                embedding = self.extract_features(aligned_face)

                # Match directly (no consistency threshold)
                match = self.match_face(embedding, self.match_threshold)

                x, y, w, h = face
                if match:
                    recognized_names.append(match)
                    
            except Exception as e:
                print(f"Error processing face: {e}")

        return display_frame, recognized_names


    def save_database(self, file_path: str) -> None:
        """
        Save the face database to a JSON file
        
        Parameters
        ----------
        file_path : str
            Path to save the database
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(self.face_database, f)
            print(f"Database saved to {file_path}")
        except Exception as e:
            print(f"Error saving database: {e}")

    def load_database(self, file_path: str) -> None:
        """
        Load the face database from a JSON file
        
        Parameters
        ----------
        file_path : str
            Path to load the database from
        """
        try:
            with open(file_path, 'r') as f:
                loaded_data = json.load(f)
                
            # Check and validate embeddings
            valid_data = {}
            
            # Set embedding dimension from first valid entry if not already set
            if self.embedding_dim is None and loaded_data:
                for ID, embeddings in loaded_data.items():
                    if embeddings and isinstance(embeddings, list):
                        if isinstance(embeddings[0], list) and embeddings[0]:
                            self.embedding_dim = len(embeddings[0])
                            print(f"Setting embedding dimension from database: {self.embedding_dim}")
                            break
                        elif not isinstance(embeddings[0], list) and embeddings:
                            self.embedding_dim = len(embeddings)
                            print(f"Setting embedding dimension from database: {self.embedding_dim}")
                            break
            
            # Validate each entry
            for ID, embeddings in loaded_data.items():
                if not embeddings:
                    continue
                    
                if isinstance(embeddings, list):
                    if isinstance(embeddings[0], list):  # Multiple embeddings
                        valid_embeddings = []
                        for emb in embeddings:
                            if emb and isinstance(emb, list) and len(emb) == self.embedding_dim:
                                valid_embeddings.append(emb)
                            else:
                                print(f"Skipping invalid embedding for ID {ID}")
                        
                        if valid_embeddings:
                            valid_data[ID] = valid_embeddings
                    else:  # Single embedding
                        if len(embeddings) == self.embedding_dim:
                            valid_data[ID] = [embeddings]  # Convert to list of embeddings format
                        else:
                            print(f"Skipping entry for ID {ID} with incorrect dimension")
            
            self.face_database = valid_data
            print(f"Database loaded from {file_path} with {len(valid_data)} valid entries")
        except Exception as e:
            print(f"Error loading database: {e}")
