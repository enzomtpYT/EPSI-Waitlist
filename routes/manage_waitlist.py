from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database

manage_waitlist_bp = Blueprint('manage_waitlist', __name__)

@manage_waitlist_bp.route("/admin/manage_waitlist/<int:id_event>", methods=['GET', 'POST'])
def manage_waitlist(id_event):
    event, error = database.get_event(id_event)
    participants, error = database.get_event_participant(id_event)
    candidates, error = database.get_event_candidates(id_event)
    existing_interviews = {}
    
    for participant in participants:
        b, error = database.get_candidate_from_event_participants_inverviews(id_event, participant['id_participant'])
        if error is not None:
            flash(error, 'danger')
            return redirect('/')
        existing_interviews[participant['id_participant']] = []
        for row in b:
            existing_interviews[participant['id_participant']].append(row['id_candidate'])
    print(f'------EXISTING------\n{existing_interviews}\n------EXISTING------')

    if request.method == 'POST':
        form_data = request.form.to_dict(flat=False)
        error = None
        
        print(f'------FORM DATA------\n{form_data}\n------FORM DATA------')

        for id_participant, all_candidates in form_data.items():
            for id_candidate in all_candidates:
                if int(id_candidate) in existing_interviews[int(id_participant)]:
                    continue
                else:
                    error = database.create_interview(id_event, id_participant, id_candidate)
                if error is not None:
                    break
            if error is not None:
                break

        if error is None:
            flash('Entretien créé avec succès.', 'success')
            return redirect(url_for('manage_waitlist.manage_waitlist', id_event=id_event))
        else:
            flash(error, 'danger')
            return redirect(url_for('manage_waitlist.manage_waitlist', id_event=id_event))

    return render_template('manage_waitlist.html', event=event, participants=participants, candidates=candidates, existing_interviews=existing_interviews)