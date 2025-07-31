import cv2
import face_recognition
import numpy as np
import os
from PIL import Image
import json
from database.models import Student, db

class FaceRecognitionSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_student_ids = []
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load all registered student faces from database"""
        students = Student.query.filter(Student.face_encoding.isnot(None)).all()
        
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_student_ids = []
        
        for student in students:
            encoding = student.get_face_encoding()
            if encoding is not None:
                self.known_face_encodings.append(encoding)
                self.known_face_names.append(student.name)
                self.known_student_ids.append(student.id)
    
    def register_face(self, image_path, student_id):
        """Register a new face for a student"""
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Find face encodings
            face_encodings = face_recognition.face_encodings(image)
            
            if len(face_encodings) == 0:
                return False, "No face found in the image"
            
            if len(face_encodings) > 1:
                return False, "Multiple faces found. Please use an image with only one face"
            
            # Get the face encoding
            face_encoding = face_encodings[0]
            
            # Save to database
            student = Student.query.get(student_id)
            if student:
                student.set_face_encoding(face_encoding)
                student.photo_path = image_path
                db.session.commit()
                
                # Reload known faces
                self.load_known_faces()
                
                return True, "Face registered successfully"
            else:
                return False, "Student not found"
                
        except Exception as e:
            return False, f"Error registering face: {str(e)}"
    
    def recognize_faces_in_frame(self, frame, tolerance=0.6):
        """Recognize faces in a video frame"""
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        
        # Find face locations and encodings
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        recognized_students = []
        
        for face_encoding, face_location in zip(face_encodings, face_locations):
            # Compare with known faces
            matches = face_recognition.compare_faces(
                self.known_face_encodings, face_encoding, tolerance=tolerance
            )
            face_distances = face_recognition.face_distance(
                self.known_face_encodings, face_encoding
            )
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    student_id = self.known_student_ids[best_match_index]
                    name = self.known_face_names[best_match_index]
                    confidence = 1 - face_distances[best_match_index]
                    
                    # Scale back up face location
                    top, right, bottom, left = face_location
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    
                    recognized_students.append({
                        'student_id': student_id,
                        'name': name,
                        'confidence': confidence,
                        'location': (top, right, bottom, left)
                    })
        
        return recognized_students
    
    def draw_recognition_results(self, frame, recognized_students):
        """Draw bounding boxes and names on the frame"""
        for student in recognized_students:
            top, right, bottom, left = student['location']
            
            # Draw rectangle around face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
            # Draw label
            label = f"{student['name']} ({student['confidence']:.2f})"
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, label, (left + 6, bottom - 6), 
                       cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        return frame

class AttendanceTracker:
    def __init__(self):
        self.face_recognition_system = FaceRecognitionSystem()
        self.attendance_buffer = {}  # Buffer to avoid duplicate entries
        self.buffer_timeout = 10  # seconds
    
    def mark_attendance(self, session_id, recognized_students):
        """Mark attendance for recognized students"""
        from database.models import Attendance, AttendanceSession
        from datetime import datetime, timedelta
        
        marked_students = []
        current_time = datetime.utcnow()
        
        for student_data in recognized_students:
            student_id = student_data['student_id']
            confidence = student_data['confidence']
            
            # Check if already marked recently (avoid duplicates)
            buffer_key = f"{session_id}_{student_id}"
            if buffer_key in self.attendance_buffer:
                last_marked = self.attendance_buffer[buffer_key]
                if (current_time - last_marked).seconds < self.buffer_timeout:
                    continue
            
            # Check if attendance already exists for this session
            existing_attendance = Attendance.query.filter_by(
                student_id=student_id,
                session_id=session_id
            ).first()
            
            if not existing_attendance:
                # Create new attendance record
                attendance = Attendance(
                    student_id=student_id,
                    session_id=session_id,
                    confidence_score=confidence,
                    status='present'
                )
                
                db.session.add(attendance)
                marked_students.append(student_data)
                
                # Update buffer
                self.attendance_buffer[buffer_key] = current_time
        
        if marked_students:
            db.session.commit()
        
        return marked_students

def process_uploaded_image(file_path):
    """Process uploaded image for face registration"""
    try:
        # Load and validate image
        image = cv2.imread(file_path)
        if image is None:
            return False, "Invalid image file"
        
        # Convert to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Check for faces
        face_locations = face_recognition.face_locations(rgb_image)
        
        if len(face_locations) == 0:
            return False, "No face detected in the image"
        
        if len(face_locations) > 1:
            return False, "Multiple faces detected. Please upload an image with only one face"
        
        return True, "Image is valid for face registration"
        
    except Exception as e:
        return False, f"Error processing image: {str(e)}"