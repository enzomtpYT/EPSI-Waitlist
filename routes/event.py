from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database
from lib.database import get_event_interviews

event_bp = Blueprint('event', __name__)

@event_bp.route("/admin/event")
def event():
    return render_template('event.html')

@event_bp.route("/admin/manage_event/event/<int:id_event>", methods=['GET', 'POST'])
def edit_event(id_event):
    event, error = database.get_event(id_event)

    if request.method == 'POST':
        name = request.form['name_event']
        date = request.form['date_event']
        # year = request.form['year_event']
        error = None

        if not name:
            error = 'Le nom est obligatoire.'
        elif not date:
            error = 'La date est obligatoire.'

        if error is None:
            error = database.edit_event(name, date, id_event)
            if error is None:
                flash("Événement mis à jour avec succès!", "success")
                return redirect(url_for('event.edit_event', id_event=id_event))
            else:
                flash(f"Erreur lors de la mise à jour de l'Événement: {error}", "danger")
                return redirect(url_for('event.edit_event', id_event=id_event))
    return render_template('event.html', event=event)

@event_bp.route("/admin/manage_event/event/<int:id_event>/interviews", methods=['GET'])
def view_interviews(id_event):
    event, interviews, error = get_event_interviews(id_event)
    if error:
        flash(error, "danger")
        return redirect(url_for('event.edit_event', id_event=id_event))
    return render_template('interviews.html', interviews=interviews, event=event, event_id=id_event)

@event_bp.route("/admin/manage_event/event/<int:id_event>/delete", methods=['POST'])
def delete_event(id_event):
    database.delete_event(id_event)
    return redirect(url_for('manage_event.manage_event'))