from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)

class TimetableEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day = db.Column(db.String(10), nullable=False)  # e.g. Monday
    subject = db.Column(db.String(100), nullable=False)
    class_name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    admission_number = db.Column(db.String(50), unique=True, nullable=False)
    class_name = db.Column(db.String(50), nullable=False)

class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    date = db.Column(db.Date)
    status = db.Column(db.String(10))  # 'Present' or 'Absent'

class LessonProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_name = db.Column(db.String(100))
    progress = db.Column(db.Integer)  # e.g., from 0 to 100
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class LessonPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    class_name = db.Column(db.String(100))
    subject = db.Column(db.String(100))
    topic = db.Column(db.String(200))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    completed = db.Column(db.Boolean, default=False)

    teacher = db.relationship('User', backref='lesson_plans')
