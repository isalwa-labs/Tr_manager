# DigiTR - Digital Teacher's Resource 📚

![DigiTR Dashboard](screenshots/dashboard.png)

A modern, intuitive classroom management system designed specifically for teachers. DigiTR streamlines daily teaching activities, from attendance tracking to lesson planning, all in one elegant platform.

## ✨ Features

### 📊 Smart Dashboard
- Real-time attendance analytics
- Class performance overview
- Quick access to daily schedules
- Personalized insights and reports

### 👥 Student Management
- Comprehensive student profiles
- Bulk import via CSV
- Attendance tracking
- Performance monitoring
- Class-wise organization

### 📅 Timetable Management
- Interactive weekly schedule
- Easy class assignment
- Conflict detection
- Mobile-responsive view

### 📝 Lesson Planning
- Create and organize lesson plans
- Track curriculum progress
- Set learning objectives
- Resource attachment support

### 📈 Analytics & Reports
- Attendance patterns
- Performance trends
- Exportable reports
- Visual data representation

## 🚀 Technology Stack

- **Frontend:**
  - HTML5, CSS3, JavaScript
  - Bootstrap 5
  - Material Design Icons
  - Chart.js for analytics

- **Backend:**
  - Python 3.11
  - Flask Framework
  - SQLAlchemy ORM
  - Flask-Login for authentication

- **Database:**
  - SQLite (Development)
  - PostgreSQL (Production)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/diji_tr.git
cd diji_tr
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask db upgrade
```

5. Run the development server:
```bash
flask run
```

## 🎯 Project Structure

```
diji_tr/
├── app/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   ├── templates/
│   │   ├── components/
│   │   ├── auth/
│   │   └── *.html
│   ├── __init__.py
│   ├── models.py
│   └── routes.py
├── migrations/
├── tests/
├── venv/
├── config.py
├── requirements.txt
└── README.md
```

## 🎨 Theme Support

DigiTR comes with both light and dark themes, automatically adapting to user preferences:

- 🌙 Dark Theme: Modern, eye-friendly dark mode
- ☀️ Light Theme: Clean, professional light mode
- 🔄 Persistent theme settings
- 💾 Local storage saving

## 🔐 Security Features

- Secure user authentication
- Password hashing
- Session management
- CSRF protection
- Input sanitization
- Role-based access control

## 📱 Responsive Design

- Mobile-first approach
- Adaptive layouts
- Touch-friendly interfaces
- Collapsible sidebar
- Responsive data tables

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch:
```bash
git checkout -b feature/AmazingFeature
```
3. Commit your changes:
```bash
git commit -m 'Add some AmazingFeature'
```
4. Push to the branch:
```bash
git push origin feature/AmazingFeature
```
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙌 Acknowledgments

- Material Design Icons for beautiful iconography
- Bootstrap team for the amazing framework
- Flask community for excellent documentation
- All contributors who have helped shape DigiTR

## 📧 Contact

- Project Link: https://github.com/yourusername/diji_tr
- Portfolio: https://yourportfolio.com
- LinkedIn: https://linkedin.com/in/yourusername

---

Made with ❤️ by [Your Name]