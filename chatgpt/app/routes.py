from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date, datetime
from werkzeug.utils import secure_filename
import csv
import io
from os import abort

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    from .models import Student, LessonPlan, TimetableEntry
    from . import db
    # Get current date
    current_date = date.today()
    
    # Get total students
    total_students = Student.query.count()
    
    # Get today's classes
    today_classes = TimetableEntry.query.filter_by(
        teacher_id=current_user.id,
        day=current_date.strftime('%A')
    ).count()
    
    # Get active lessons
    active_lessons = LessonPlan.query.filter_by(
        teacher_id=current_user.id,
        completed=False
    ).count()
    
    # Get recent activities (last 5)
    recent_activities = []  # You'll need to implement your activity tracking
    
    # Get unique class names
    class_names = db.session.query(Student.class_name).distinct().all()
    class_names = [c[0] for c in class_names]

    return render_template('dashboard.html',
        current_date=current_date,
        total_students=total_students,
        today_classes=today_classes,
        active_lessons=active_lessons,
        recent_activities=recent_activities,
        class_names=class_names
    )

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
    from .models import Student, AttendanceRecord
    from . import db

    # Changed to left outer join and added order by for attendance records
    student = (
        Student.query
        .outerjoin(AttendanceRecord)  # Use outerjoin instead of join
        .filter(Student.id == student_id)
        .first_or_404()
    )

    if request.method == 'POST':
        # Validate unique admission number except for current student
        existing = Student.query.filter(
            Student.admission_number == request.form.get('admission_number'),
            Student.id != student_id
        ).first()
        
        if existing:
            flash('Admission number already exists', 'warning')
            return render_template('edit_student.html', student=student)

        student.name = request.form.get('name')
        student.admission_number = request.form.get('admission_number')
        student.class_name = request.form.get('class_name')
        
        try:
            db.session.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('main.manage_students'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the student.', 'danger')
            return render_template('edit_student.html', student=student)

    # Get attendance records separately
    attendance_records = (
        AttendanceRecord.query
        .filter_by(student_id=student.id)
        .order_by(AttendanceRecord.date.desc())
        .all()
    )

    return render_template('edit_student.html', 
                         student=student, 
                         attendance_records=attendance_records)

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

@main.route('/lesson-plans', methods=['GET', 'POST'])
@login_required
def lesson_plans():
    from .models import LessonPlan
    from . import db

    if request.method == 'POST':
        class_name = request.form.get('class_name')
        subject = request.form.get('subject')
        topic = request.form.get('topic')
        start = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()

        plan = LessonPlan(
            teacher_id=current_user.id,
            class_name=class_name,
            subject=subject,
            topic=topic,
            start_date=start,
            end_date=end,
            completed=False
        )
        db.session.add(plan)
        db.session.commit()
        flash('Lesson plan added!', 'success')
        return redirect(url_for('main.lesson_plans'))

    plans = LessonPlan.query.filter_by(teacher_id=current_user.id).order_by(LessonPlan.start_date).all()
    current_date = date.today()
    return render_template('lesson_plans.html', plans=plans,current_date=current_date)


@main.route('/lesson-plans/complete/<int:plan_id>', methods=['POST'])
@login_required
def mark_lesson_complete(plan_id):
    from .models import LessonPlan
    from . import db

    plan = LessonPlan.query.get_or_404(plan_id)
    if plan.teacher_id != current_user.id:
        abort(403)

    plan.completed = True
    db.session.commit()
    flash('Lesson marked as complete.', 'success')
    return redirect(url_for('main.lesson_plans'))

@main.route('/reports/dashboard')
@login_required
def reports_dashboard():
    from .models import LessonPlan, Student, AttendanceRecord
    from . import db
    teacher_id = current_user.id

    # Attendance Summary
    attendance_summary = []
    classes = db.session.query(Student.class_name).distinct().all()

    for (class_name,) in classes:
        students = Student.query.filter_by(class_name=class_name).all()
        total_days = 0
        total_present = 0

        for student in students:
            total = AttendanceRecord.query.filter_by(student_id=student.id).count()
            present = AttendanceRecord.query.filter_by(student_id=student.id, status='Present').count()
            total_days += total
            total_present += present

        percent = (total_present / total_days * 100) if total_days > 0 else 0
        attendance_summary.append({
            'class_name': class_name,
            'attendance_percent': round(percent, 2),
        })

    # Lesson Plan Summary
    lesson_plans = LessonPlan.query.filter_by(teacher_id=teacher_id).all()
    lesson_summary = {}

    for plan in lesson_plans:
        key = f"{plan.class_name} - {plan.subject}"
        if key not in lesson_summary:
            lesson_summary[key] = {'total': 0, 'completed': 0}
        lesson_summary[key]['total'] += 1
        if plan.completed:
            lesson_summary[key]['completed'] += 1

    lesson_summary_data = []
    for key, data in lesson_summary.items():
        percent = (data['completed'] / data['total'] * 100) if data['total'] > 0 else 0
        lesson_summary_data.append({
            'group': key,
            'percent_complete': round(percent, 2),
        })

    return render_template(
        'reports_dashboard.html',
        attendance_summary=attendance_summary,
        lesson_summary=lesson_summary_data
    )
