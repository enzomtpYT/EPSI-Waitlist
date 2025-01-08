from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database

manage_waitlist_bp = Blueprint('manage_waitlist', __name__)

@manage_waitlist_bp.route("/admin/manage_waitlist/<int:id_event>", methods=['GET', 'POST'])
def manage_waitlist(id_event):
    event, error = database.get_event(id_event)
    participants, error = database.get_all_participants()
    candidates, error = database.get_all_candidates()

    if request.method == 'POST':
        id_participant = request.form['participant']
        id_candidate = request.form['candidate']
        error = None

        if not id_participant:
            error = 'Le participant est obligatoire.'
        elif not id_candidate:
            error = 'Le candidat est obligatoire.'

        if error is None:
            error = database.create_interview(id_event, id_participant, id_candidate)
            if error is None:
                flash('Entretien créé avec succès.', 'success')
                return redirect(url_for('manage_waitlist.manage_waitlist', id_event=id_event))
            else:
                flash(error, 'danger')
                return redirect(url_for('manage_waitlist.manage_waitlist', id_event=id_event))

    return render_template('manage_waitlist.html', event=event, participants=participants, candidates=candidates)