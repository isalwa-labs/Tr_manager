from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import date
from werkzeug.utils import secure_filename
import csv
import io

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main.route('/attendance/<class_name>', methods=['GET', 'POST'])
@login_required
def attendance(class_name):
    from .models import Student, AttendanceRecord
    from . import db
    from datetime import date

    students = Student.query.filter_by(class_name=class_name).all()
    today = date.today()

    if request.method == 'POST':
        selected_date = request.form.get('date')
        for student in students:
            marked = request.form.get(f'status_{student.id}')
            status = 'Present' if marked else 'Absent'

            # Avoid duplicates
            existing = AttendanceRecord.query.filter_by(student_id=student.id, date=selected_date).first()
            if not existing:
                record = AttendanceRecord(
                    student_id=student.id,
                    date=selected_date,
                    status=status
                )
                db.session.add(record)
        db.session.commit()
        flash('Attendance saved.', 'success')
        return redirect(url_for('main.attendance', class_name=class_name))

    return render_template('attendance.html', students=students, class_name=class_name, date=today.isoformat())

@main.route('/attendance/history/<class_name>')
@login_required
def attendance_history(class_name):
    from .models import Student, AttendanceRecord
    from . import db

    records = (
        db.session.query(AttendanceRecord, Student)
        .join(Student)
        .filter(Student.class_name == class_name)
        .order_by(AttendanceRecord.date.desc())
        .all()
    )

    grouped = {}
    for record, student in records:
        if record.date not in grouped:
            grouped[record.date] = []
        grouped[record.date].append({
            "name": student.name,
            "admission": student.admission_number,
            "status": record.status
        })

    return render_template('attendance_history.html', class_name=class_name, grouped=grouped)

@main.route('/attendance/report/<class_name>')
@login_required
def attendance_report(class_name):
    from .models import Student, AttendanceRecord
    from . import db

    students = Student.query.filter_by(class_name=class_name).all()
    report_data = []

    for student in students:
        total = AttendanceRecord.query.filter_by(student_id=student.id).count()
        present = AttendanceRecord.query.filter_by(student_id=student.id, status='Present').count()
        percent = (present / total * 100) if total > 0 else 0
        report_data.append({
            "name": student.name,
            "admission": student.admission_number,
            "total": total,
            "present": present,
            "percent": round(percent, 2)
        })

    return render_template('attendance_report.html', class_name=class_name, report=report_data)


@main.route('/students', methods=['GET', 'POST'])
@login_required
def manage_students():
    from .models import Student
    from . import db

    if request.method == 'POST':
        if 'csv_file' in request.files:
            # CSV Upload
            file = request.files['csv_file']
            if file.filename.endswith('.csv'):
                stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                reader = csv.DictReader(stream)
                count = 0
                for row in reader:
                    name = row.get('name')
                    admission_number = row.get('admission_number')
                    class_name = row.get('class_name')
                    if name and admission_number and class_name:
                        exists = Student.query.filter_by(admission_number=admission_number).first()
                        if not exists:
                            student = Student(
                                name=name.strip(),
                                admission_number=admission_number.strip(),
                                class_name=class_name.strip()
                            )
                            db.session.add(student)
                            count += 1
                db.session.commit()
                flash(f"{count} students added from CSV", "success")
            else:
                flash("Please upload a valid CSV file.", "danger")

        else:
            # Manual add
            name = request.form.get('name')
            admission_number = request.form.get('admission_number')
            class_name = request.form.get('class_name')
            if name and admission_number and class_name:
                exists = Student.query.filter_by(admission_number=admission_number).first()
                if not exists:
                    student = Student(name=name, admission_number=admission_number, class_name=class_name)
                    db.session.add(student)
                    db.session.commit()
                    flash("Student added successfully", "success")
                else:
                    flash("Admission number already exists", "warning")
            else:
                flash("All fields are required", "danger")

    students = Student.query.order_by(Student.class_name, Student.name).all()
    return render_template("students.html", students=students)

@main.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    from .models import Student
    from . import db

    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        student.name = request.form.get('name')
        student.admission_number = request.form.get('admission_number')
        student.class_name = request.form.get('class_name')

        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('main.manage_students'))

    return render_template('edit_student.html', student=student)


@main.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    from .models import Student
    from . import db

    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted.', 'warning')
    return redirect(url_for('main.manage_students'))
