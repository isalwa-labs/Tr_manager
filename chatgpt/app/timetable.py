from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .models import db, TimetableEntry
from os import abort

timetable = Blueprint('timetable', __name__)

@timetable.route('/dashboard/timetable')
@login_required
def view_timetable():
    entries = TimetableEntry.query.filter_by(teacher_id=current_user.id).all()
    return render_template('timetable.html', entries=entries)

@timetable.route('/dashboard/timetable/add', methods=['GET', 'POST'])
@login_required
def add_entry():
    if request.method == 'POST':
        new_entry = TimetableEntry(
            teacher_id=current_user.id,
            day=request.form['day'],
            subject=request.form['subject'],
            class_name=request.form['class_name'],
            start_time=request.form['start_time'],
            end_time=request.form['end_time']
        )
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('timetable.view_timetable'))
    return render_template('add_timetable.html')

@timetable.route('/dashboard/timetable/edit/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    entry = TimetableEntry.query.get_or_404(entry_id)
    if entry.teacher_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        entry.day = request.form['day']
        entry.subject = request.form['subject']
        entry.class_name = request.form['class_name']
        entry.start_time = request.form['start_time']
        entry.end_time = request.form['end_time']
        db.session.commit()
        return redirect(url_for('timetable.view_timetable'))
    return render_template('edit_timetable.html', entry=entry)

@timetable.route('/dashboard/timetable/delete/<int:entry_id>')
@login_required
def delete_entry(entry_id):
    entry = TimetableEntry.query.get_or_404(entry_id)
    if entry.teacher_id != current_user.id:
        abort(403)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('timetable.view_timetable'))
