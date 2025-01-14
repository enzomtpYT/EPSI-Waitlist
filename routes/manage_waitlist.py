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

    def transform_data(data):
        transformed_data = {}
        for key, values in data.items():
            new_key = int(key.replace('part', ''))
            new_values = [int(value.replace('cand', '')) for value in values]
            transformed_data[new_key] = new_values
        return transformed_data

    if request.method == 'POST':
        form_data = request.form.to_dict(flat=False)
        form_data = transform_data(form_data)
        error = None
        
        # Detect if all interviews are removed from a participant
        removed_participants = set(existing_interviews.keys()) - set(form_data.keys())
        for id_participant in removed_participants:
            form_data[id_participant] = []
        
        changes = {'removed': {}, 'added': {}}
        for id_participant, all_candidates in form_data.items():
            changes['removed'][id_participant] = list(set(existing_interviews[int(id_participant)]) - set(all_candidates))
            changes['added'][id_participant] = list(set(all_candidates) - set(existing_interviews[int(id_participant)]))
        
        print(f'------CHANGES------\n{changes}\n------CHANGES------')
        
        for id_participant, candidates in changes['removed'].items():
            for id_candidate in candidates:
                interview, error = database.get_interview_by_candidate_event_participant(id_candidate, id_event, id_participant)
                error = database.delete_interview(interview['id_interview'])
                if error is not None:
                    break
            if error is not None:
                break
        
        for id_participant, candidates in changes['added'].items():
            for id_candidate in candidates:
                error = database.create_interview(id_event, id_participant, id_candidate)
                if error is not None:
                    break
            if error is not None:
                break

        if error is None:
            flash('Entretien modifié, avec succès.', 'success')
            return redirect(url_for('manage_waitlist.manage_waitlist', id_event=id_event))
        else:
            flash(error, 'danger')
            return redirect(url_for('manage_waitlist.manage_waitlist', id_event=id_event))

    return render_template('manage_waitlist.html', event=event, participants=participants, candidates=candidates, existing_interviews=existing_interviews)