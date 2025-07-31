from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, Response
from database.models import db, Student, Teacher, Class, Enrollment, AttendanceSession, Attendance, ExamController
from utils.face_recognition_utils import FaceRecognitionSystem, AttendanceTracker, process_uploaded_image
import cv2
import os
from datetime import datetime, date
import json
from werkzeug.utils import secure_filename
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Initialize database
db.init_app(app)

# Global variables for camera and attendance tracking
camera = None
attendance_tracker = AttendanceTracker()
current_session_id = None

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.before_first_request
def create_tables():
    db.create_all()
    
    # Create sample data if database is empty
    if Student.query.count() == 0:
        create_sample_data()

def create_sample_data():
    """Create sample data for testing"""
    # Sample teacher
    teacher = Teacher(
        teacher_id='T001',
        name='Dr. John Smith',
        email='john.smith@university.edu',
        department='Computer Science'
    )
    db.session.add(teacher)
    db.session.flush()
    
    # Sample class
    class_obj = Class(
        class_code='CS101',
        name='Introduction to Programming',
        subject='Computer Science',
        teacher_id=teacher.id,
        schedule_time='MWF 10:00-11:00',
        room='Room 101'
    )
    db.session.add(class_obj)
    db.session.flush()
    
    # Sample students
    students_data = [
        {'student_id': 'S001', 'name': 'Alice Johnson', 'email': 'alice@student.edu'},
        {'student_id': 'S002', 'name': 'Bob Wilson', 'email': 'bob@student.edu'},
        {'student_id': 'S003', 'name': 'Carol Davis', 'email': 'carol@student.edu'},
    ]
    
    for student_data in students_data:
        student = Student(**student_data)
        db.session.add(student)
        db.session.flush()
        
        # Enroll student in class
        enrollment = Enrollment(student_id=student.id, class_id=class_obj.id)
        db.session.add(enrollment)
    
    # Sample exam controller
    controller = ExamController(
        controller_id='C001',
        name='Prof. Sarah Brown',
        email='sarah.brown@university.edu',
        position='Examination Controller'
    )
    db.session.add(controller)
    
    db.session.commit()

# Routes for different views

@app.route('/')
def index():
    return render_template('index.html')

# Student View Routes
@app.route('/student')
def student_dashboard():
    return render_template('student/dashboard.html')

@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        email = request.form['email']
        
        # Check if student already exists
        existing_student = Student.query.filter_by(student_id=student_id).first()
        if existing_student:
            flash('Student ID already exists', 'error')
            return redirect(url_for('student_register'))
        
        # Create new student
        student = Student(student_id=student_id, name=name, email=email)
        db.session.add(student)
        db.session.commit()
        
        flash('Student registered successfully', 'success')
        return redirect(url_for('student_register_face', student_id=student.id))
    
    return render_template('student/register.html')

@app.route('/student/register_face/<int:student_id>', methods=['GET', 'POST'])
def student_register_face(student_id):
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'POST':
        if 'photo' not in request.files:
            flash('No photo uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['photo']
        if file.filename == '':
            flash('No photo selected', 'error')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(f"student_{student_id}_{file.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Process image and register face
            valid, message = process_uploaded_image(file_path)
            if valid:
                face_system = FaceRecognitionSystem()
                success, result_message = face_system.register_face(file_path, student_id)
                if success:
                    flash('Face registered successfully', 'success')
                    return redirect(url_for('student_dashboard'))
                else:
                    flash(result_message, 'error')
            else:
                flash(message, 'error')
    
    return render_template('student/register_face.html', student=student)

@app.route('/student/attendance/<student_id>')
def student_attendance(student_id):
    student = Student.query.filter_by(student_id=student_id).first_or_404()
    
    # Get attendance records
    attendances = db.session.query(Attendance, AttendanceSession, Class).join(
        AttendanceSession, Attendance.session_id == AttendanceSession.id
    ).join(
        Class, AttendanceSession.class_id == Class.id
    ).filter(Attendance.student_id == student.id).order_by(
        AttendanceSession.session_date.desc()
    ).all()
    
    return render_template('student/attendance.html', student=student, attendances=attendances)

# Teacher View Routes
@app.route('/teacher')
def teacher_dashboard():
    teachers = Teacher.query.all()
    return render_template('teacher/dashboard.html', teachers=teachers)

@app.route('/teacher/<int:teacher_id>/classes')
def teacher_classes(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    classes = Class.query.filter_by(teacher_id=teacher_id).all()
    return render_template('teacher/classes.html', teacher=teacher, classes=classes)

@app.route('/teacher/start_session/<int:class_id>')
def start_attendance_session(class_id):
    global current_session_id
    
    class_obj = Class.query.get_or_404(class_id)
    
    # Create new attendance session
    session_obj = AttendanceSession(
        class_id=class_id,
        session_date=date.today(),
        start_time=datetime.utcnow(),
        created_by=class_obj.teacher_id
    )
    db.session.add(session_obj)
    db.session.commit()
    
    current_session_id = session_obj.id
    
    return render_template('teacher/attendance_session.html', 
                         class_obj=class_obj, session=session_obj)

@app.route('/teacher/end_session/<int:session_id>')
def end_attendance_session(session_id):
    global current_session_id
    
    session_obj = AttendanceSession.query.get_or_404(session_id)
    session_obj.end_time = datetime.utcnow()
    session_obj.is_active = False
    db.session.commit()
    
    current_session_id = None
    
    flash('Attendance session ended', 'success')
    return redirect(url_for('teacher_classes', teacher_id=session_obj.created_by))

@app.route('/teacher/session_report/<int:session_id>')
def session_report(session_id):
    session_obj = AttendanceSession.query.get_or_404(session_id)
    
    # Get all enrolled students
    enrolled_students = db.session.query(Student).join(
        Enrollment, Student.id == Enrollment.student_id
    ).filter(Enrollment.class_id == session_obj.class_id).all()
    
    # Get attendance records for this session
    attendances = Attendance.query.filter_by(session_id=session_id).all()
    attendance_dict = {att.student_id: att for att in attendances}
    
    # Combine data
    report_data = []
    for student in enrolled_students:
        attendance = attendance_dict.get(student.id)
        report_data.append({
            'student': student,
            'attendance': attendance,
            'status': attendance.status if attendance else 'absent'
        })
    
    return render_template('teacher/session_report.html', 
                         session=session_obj, report_data=report_data)

# Controller View Routes
@app.route('/controller')
def controller_dashboard():
    # Get overall statistics
    total_students = Student.query.count()
    total_classes = Class.query.count()
    total_sessions = AttendanceSession.query.count()
    
    # Recent sessions
    recent_sessions = db.session.query(AttendanceSession, Class).join(
        Class, AttendanceSession.class_id == Class.id
    ).order_by(AttendanceSession.start_time.desc()).limit(10).all()
    
    return render_template('controller/dashboard.html',
                         total_students=total_students,
                         total_classes=total_classes,
                         total_sessions=total_sessions,
                         recent_sessions=recent_sessions)

@app.route('/controller/reports')
def controller_reports():
    # Attendance statistics by class
    class_stats = db.session.query(
        Class.name,
        Class.subject,
        db.func.count(AttendanceSession.id).label('total_sessions'),
        db.func.count(Attendance.id).label('total_attendances')
    ).outerjoin(
        AttendanceSession, Class.id == AttendanceSession.class_id
    ).outerjoin(
        Attendance, AttendanceSession.id == Attendance.session_id
    ).group_by(Class.id).all()
    
    return render_template('controller/reports.html', class_stats=class_stats)

@app.route('/controller/students')
def controller_students():
    students = Student.query.all()
    return render_template('controller/students.html', students=students)

# Camera and Real-time Recognition Routes
@app.route('/start_camera')
def start_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
    return jsonify({'status': 'Camera started'})

@app.route('/stop_camera')
def stop_camera():
    global camera
    if camera is not None:
        camera.release()
        camera = None
    return jsonify({'status': 'Camera stopped'})

def generate_frames():
    global camera, attendance_tracker, current_session_id
    
    while camera is not None:
        success, frame = camera.read()
        if not success:
            break
        
        # Recognize faces in frame
        recognized_students = attendance_tracker.face_recognition_system.recognize_faces_in_frame(frame)
        
        # Mark attendance if session is active
        if current_session_id and recognized_students:
            marked_students = attendance_tracker.mark_attendance(current_session_id, recognized_students)
        
        # Draw recognition results
        frame = attendance_tracker.face_recognition_system.draw_recognition_results(frame, recognized_students)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_recognized_students')
def get_recognized_students():
    """API endpoint to get currently recognized students"""
    global camera, attendance_tracker
    
    if camera is None:
        return jsonify({'students': []})
    
    success, frame = camera.read()
    if success:
        recognized_students = attendance_tracker.face_recognition_system.recognize_faces_in_frame(frame)
        return jsonify({'students': recognized_students})
    
    return jsonify({'students': []})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)