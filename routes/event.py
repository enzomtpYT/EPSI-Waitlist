from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database, api
import json
from fpdf import FPDF
from flask import make_response

event_bp = Blueprint('event', __name__)

@event_bp.route("/admin/event")
def event():
    return render_template('event.html')

@event_bp.route("/admin/manage_event/event/<int:id_event>", methods=['GET', 'POST'])
def edit_event(id_event):
    event, error = database.get_event(id_event)
    if error:
        flash(f"Erreur lors de la récupération de l'événement: {error}", "danger")
        return redirect(url_for('event.event'))

    tags, error = database.get_all_tags()

    if request.method == 'POST':
        name = request.form['name_event']
        date = request.form['date_event']
        start_time_event = request.form.get('start_time_event') or None
        end_time_event = request.form.get('end_time_event') or None
        has_timeslots = request.form.get('has_timeslots') == 'on'
        timeslots = request.form.get('timeslots')
        if timeslots:
            timeslots = json.loads(timeslots)
        tags = request.form.getlist('tags')

        error = None

        if not name:
            error = 'Le nom est obligatoire.'
        elif not date:
            error = 'La date est obligatoire.'

        if error is None:
            error = database.edit_event(name, date, id_event, has_timeslots, start_time_event, end_time_event)
            if error is None:
                # if has_timeslots:
                #     for key, timeslot in timeslots.items():
                #         start_timeslot = timeslot.get('start')
                #         end_timeslot = timeslot.get('end')
                #         nbr_spots = timeslot.get('spots')
                #         id_timeslot = timeslot.get('id')
                #         if start_timeslot and end_timeslot and nbr_spots and not id_timeslot:
                #             error = database.add_timeslot_to_event(id_event, start_timeslot, end_timeslot, nbr_spots)
                #         elif start_timeslot and end_timeslot and nbr_spots and id_timeslot:
                #             error = database.edit_timeslot(start_timeslot, end_timeslot, nbr_spots, id_timeslot)
                #         else:
                #             error = "Les champs des créneaux horaires ne sont pas correctement remplis."
                #     if error:
                #         flash(f"Erreur lors de l'ajout des créneaux horaires: {error}", "danger")
                flash("Événement mis à jour avec succès!", "success")
                return redirect(url_for('event.edit_event', id_event=id_event))
            else:
                flash(f"Erreur lors de la mise à jour de l'Événement: {error}", "danger")
                return redirect(url_for('event.edit_event', id_event=id_event))

    return render_template('event.html', event=event, tags=tags)

@event_bp.route("/admin/manage_event/event/<int:id_event>/delete_timeslot/<int:id_timeslot>", methods=['POST'])
def delete_timeslot(id_event, id_timeslot):
    error = database.delete_timeslot(id_timeslot)
    if error:
        flash(f"Erreur lors de la suppression du créneau: {error}", "danger")
    else:
        flash("Créneau supprimé avec succès!", "success")
    return redirect(url_for('event.edit_event', id_event=id_event))

@event_bp.route("/admin/manage_event/event/<int:id_event>/add_tag_event", methods=['POST'])
def add_tag_event(id_event):
    if 'add_tag' in request.form:
        id_tag = request.form['tag']
        error = database.add_tag_to_event(id_event, id_tag)
        if error:
            flash(f"Erreur lors de l'ajout du tag: {error}", "danger")
        else:
            flash("Tag ajouté avec succès!", "success")
    return redirect(url_for('event.edit_event', id_event=id_event))

@event_bp.route("/admin/manage_event/event/<int:id_event>/remove_tag_event", methods=['POST'])
def remove_tag_event(id_event):
    if 'remove_tag' in request.form:
        id_tag = request.form['tag']
        error = database.remove_tag_from_event(id_event, id_tag)
        if error:
            flash(f"Erreur lors de la suppression du tag: {error}", "danger")
        else:
            flash("Tag supprimé avec succès!", "success")

    return redirect(url_for('event.edit_event', id_event=id_event))

@event_bp.route("/admin/manage_event/event/<int:id_event>/interviews", methods=['GET'])
def view_interviews(id_event):
    event, interviews, error = database.get_event_interviews(id_event)
    if error:
        flash(error, "danger")
        return redirect(url_for('event.edit_event', id_event=id_event))
    return render_template('interviews.html', interviews=interviews, event=event, event_id=id_event)

@event_bp.route("/admin/manage_event/event/<int:id_event>/export_interviews_pdf", methods=['GET', 'POST'])
def export_interviews_pdf(id_event):
    event, interviews, error = database.get_event_interviews(id_event)
    tags, error = database.get_event_tags(id_event)
    if error:
        flash(error, "danger")
        return redirect(url_for('event.edit_event', id_event=id_event))
    # Generate PDF
    class PDF(FPDF):
        def __init__(self, name_event):
            super().__init__()
            self.name_event = name_event

        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, f'Événement : {self.name_event}', 0, 1, 'C')

    pdf = PDF(event.get('name_event', 'N/A') if event else 'N/A')
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    pdf.cell(0, 10, f"Date de l'événement : {event.get('date_event', 'N/A')}", 0, 1)
    if tags:
        tag_names = ", ".join(tag.get('name_tag', 'N/A') for tag in tags)
        pdf.cell(0, 10, f"Tags de l'événement : {tag_names}", 0, 1)
    pdf.ln(10)

    for interview in interviews:
        pdf.cell(0, 10, f"Intervevant : {interview.get('name_participant', 'N/A')}", 0, 1)
        pdf.cell(0, 10, f"Candidat : {interview.get('name_candidate', 'N/A')} {interview.get('lastname_candidate', 'N/A')}", 0, 1)
        feedback_participant = interview.get('feedback_participant')
        if feedback_participant:
            pdf.cell(0, 10, f"Feedback intervenant : {feedback_participant}", 0, 1)

        feedback_candidate = interview.get('feedback_candidate')
        if feedback_candidate:
            pdf.cell(0, 10, f"Feedback candidat : {feedback_candidate}", 0, 1)
        pdf.ln(10)

    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    return response

@event_bp.route("/admin/manage_event/event/<int:id_event>/delete", methods=['POST'])
def delete_event(id_event):
    database.delete_event(id_event)
    return redirect(url_for('manage_event.manage_event'))

@event_bp.route('/admin/manage_event/event/<int:id_event>/manage_event_participants', methods=['GET', 'POST'])
def manage_event_participants(id_event):
    return render_template('manage_event_participants.html', id_event=id_event)