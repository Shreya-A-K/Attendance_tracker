# Smart Attendance Tracking System

A comprehensive machine learning-powered attendance tracking system using computer vision and face recognition technology. Built with Flask, OpenCV, and face_recognition library.

## Features

### 🎯 Core Functionality
- **Real-time Face Recognition**: Automatic student identification using advanced computer vision
- **Multi-Role Interface**: Separate dashboards for Students, Teachers, and Examination Controllers
- **Live Camera Feed**: Real-time video processing with face detection overlay
- **Automated Attendance**: Instant attendance marking when students are recognized
- **Comprehensive Reporting**: Detailed analytics and exportable reports

### 👥 User Roles

#### 🎓 Student Portal
- Student registration and profile management
- Face photo upload and registration
- Personal attendance record viewing
- Interactive attendance statistics with charts
- Attendance history with confidence scores

#### 👨‍🏫 Teacher Portal
- Class management and session control
- Live attendance session monitoring
- Real-time face recognition feed
- Attendance report generation
- Session history and analytics

#### 👔 Controller Portal
- System-wide overview and statistics
- Administrative controls and monitoring
- Comprehensive reporting across all classes
- Student management and oversight
- System performance analytics

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy with SQLite
- **Computer Vision**: OpenCV, face_recognition, dlib
- **Frontend**: Bootstrap 5, HTML5, JavaScript
- **Charts**: Chart.js for data visualization
- **Icons**: Font Awesome

## Installation

### Prerequisites
- Python 3.8 or higher
- Webcam/Camera access
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/attendance-tracking-system.git
cd attendance-tracking-system
```

### Step 2: Create Virtual Environment
```bash
python -m venv attendance_env
source attendance_env/bin/activate  # On Windows: attendance_env\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database
```bash
python app.py
```
The application will automatically create the database and sample data on first run.

### Step 5: Run the Application
```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## Usage Guide

### Initial Setup

1. **Start the Application**: Run `python app.py`
2. **Access the System**: Navigate to `http://localhost:5000`
3. **Choose Your Role**: Select Student, Teacher, or Controller from the main page

### Student Workflow

1. **Register**: Click "Student Portal" → "Register New Student"
2. **Upload Photo**: After registration, upload a clear face photo
3. **View Attendance**: Use your Student ID to check attendance records

### Teacher Workflow

1. **Select Profile**: Choose your teacher profile from the dashboard
2. **Manage Classes**: View and manage your assigned classes
3. **Start Session**: Click "Start Attendance Session" for a class
4. **Monitor Live**: Use the camera feed to track real-time attendance
5. **End Session**: Stop the session and view reports

### Controller Workflow

1. **System Overview**: View comprehensive system statistics
2. **Generate Reports**: Access detailed attendance analytics
3. **Manage Students**: Oversee student registrations and data
4. **Monitor System**: Track system performance and alerts

## System Architecture

```
attendance-tracking-system/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── database/
│   └── models.py         # Database models and relationships
├── utils/
│   └── face_recognition_utils.py  # Computer vision utilities
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Main landing page
│   ├── student/         # Student portal templates
│   ├── teacher/         # Teacher portal templates
│   └── controller/      # Controller portal templates
└── static/
    ├── css/            # Custom stylesheets
    ├── js/             # JavaScript files
    └── uploads/        # Student face photos
```

## Database Schema

### Key Models
- **Student**: Student profiles and face encodings
- **Teacher**: Teacher information and assignments
- **Class**: Course information and schedules
- **AttendanceSession**: Individual class sessions
- **Attendance**: Student attendance records
- **ExamController**: Administrative users

## API Endpoints

### Camera Control
- `GET /start_camera` - Initialize camera feed
- `GET /stop_camera` - Stop camera feed
- `GET /video_feed` - Live video stream
- `GET /get_recognized_students` - Current recognized students

### Student Routes
- `GET/POST /student/register` - Student registration
- `GET/POST /student/register_face/<id>` - Face photo upload
- `GET /student/attendance/<student_id>` - Attendance records

### Teacher Routes
- `GET /teacher/<id>/classes` - Teacher's classes
- `GET /teacher/start_session/<class_id>` - Start attendance session
- `GET /teacher/end_session/<session_id>` - End attendance session

### Controller Routes
- `GET /controller` - Controller dashboard
- `GET /controller/reports` - System reports
- `GET /controller/students` - Student management

## Configuration

### Environment Variables
Create a `.env` file for production:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///attendance_system.db
UPLOAD_FOLDER=static/uploads
```

### Face Recognition Settings
- **Tolerance**: Adjust in `face_recognition_utils.py` (default: 0.6)
- **Recognition Frequency**: Modify polling interval in templates
- **Confidence Threshold**: Configure minimum confidence scores

## Troubleshooting

### Common Issues

1. **Camera Not Working**
   - Check camera permissions
   - Ensure no other applications are using the camera
   - Verify OpenCV installation

2. **Face Recognition Errors**
   - Install dlib properly: `pip install dlib`
   - Use clear, well-lit photos for registration
   - Ensure single face per registration photo

3. **Database Issues**
   - Delete `attendance_system.db` to reset
   - Check SQLAlchemy version compatibility
   - Verify write permissions in project directory

### Performance Optimization

- **Frame Processing**: Reduce video resolution for better performance
- **Recognition Frequency**: Increase polling interval for slower systems
- **Database**: Use PostgreSQL for production environments

## Development

### Adding New Features

1. **Database Changes**: Update models in `database/models.py`
2. **Routes**: Add new endpoints in `app.py`
3. **Templates**: Create corresponding HTML templates
4. **Utilities**: Extend functionality in `utils/`

### Testing

```bash
# Run basic functionality test
python -c "from utils.face_recognition_utils import FaceRecognitionSystem; print('System OK')"
```

## Security Considerations

- **Face Data**: Encrypted storage of face encodings
- **Session Management**: Secure session handling
- **File Uploads**: Validated image file uploads
- **Database**: Parameterized queries to prevent SQL injection

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **face_recognition** library by Adam Geitgey
- **OpenCV** for computer vision capabilities
- **Flask** web framework
- **Bootstrap** for responsive UI design

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

---

**Note**: This system is designed for educational and small-scale institutional use. For large-scale deployment, consider additional security measures and performance optimizations.