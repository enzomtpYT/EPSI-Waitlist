from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database, api

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
    event_tags, error = database.get_event_tags(id_event)

    if request.method == 'POST':
        name = request.form['name_event']
        date = request.form['date_event']
        tags = request.form.getlist('tags')
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

    return render_template('event.html', event=event, tags=tags, event_tags=event_tags)

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

@event_bp.route("/admin/manage_event/event/<int:id_event>/delete", methods=['POST'])
def delete_event(id_event):
    database.delete_event(id_event)
    return redirect(url_for('manage_event.manage_event'))

@event_bp.route('/admin/manage_event/event/<int:id_event>/manage_event_participants', methods=['GET', 'POST', 'HEAD'])
def manage_event_participants(id_event):
    datas, error = api.get_event_participants(id_event)
    if error:
        flash(error, "danger")
        return redirect(url_for('event.edit_event', id_event=id_event))
    if request.method == 'POST':
        changes = {'candidates': {'removed':[],'added':[], 'edited':[]}, 'participants': {'removed':[],'added':[]}}

        dbcandidates = datas['candidates']
        dbparticipants = datas['participants']

        form = {
            "candidates": [],
            "participants": []
        }

        for fcandidate in request.form.getlist('candidates'):
            prio = request.form[f"priority_{fcandidate}"]
            if prio == '':
                prio = '1'
            form['candidates'].append({"id_candidate": int(fcandidate), "priority": int(prio)})
        for fparticipant in request.form.getlist('participants'):
            form['participants'].append({"id_participant": int(fparticipant)})

        for formcandidates in form['candidates']:
            for candid in dbcandidates:
                if formcandidates['id_candidate'] == candid['id_candidate']:
                    if formcandidates['priority'] != candid['priority']:
                        changes['candidates']['edited'].append({formcandidates['id_candidate'] : formcandidates['priority']})
                    if candid['attends'] == False:
                        changes['candidates']['added'].append({formcandidates['id_candidate'] : formcandidates['priority']})

        for dbcandid in dbcandidates:
            if dbcandid['id_candidate'] not in [formcandidate['id_candidate'] for formcandidate in form['candidates']] and dbcandid['attends'] == True:
                changes['candidates']['removed'].append(dbcandid['id_candidate'])

        for formparticipants in form['participants']:
            for part in dbparticipants:
                if formparticipants['id_participant'] == part['id_participant']:
                    if part['attends'] == False:
                        changes['participants']['added'].append(formparticipants['id_participant'])
                    break

        print(changes)

        for dbpart in dbparticipants:
            if dbpart['id_participant'] not in [formparticipant['id_participant'] for formparticipant in form['participants']] and dbpart['attends'] == True:
                changes['participants']['removed'].append(dbpart['id_participant'])

        for item in changes['candidates']['added']:
            candidate, priority = list(item.items())[0]
            error = database.create_attends(candidate, id_event, priority)
            if error:
                flash(error, "danger")
                return redirect(url_for('event.manage_event_participants', id_event=id_event))

        for candidate in changes['candidates']['removed']:
            error = database.delete_attends(candidate, id_event)
            if error:
                flash(error, "danger")
                return redirect(url_for('event.manage_event_participants', id_event=id_event))

        for item in changes['candidates']['edited']:
            candidate, priority = list(item.items())[0]
            error = database.edit_attends(candidate, id_event, priority)
            if error:
                flash(error, "danger")
                return redirect(url_for('event.manage_event_participants', id_event=id_event))

        for participant in changes['participants']['added']:
            error = database.create_participates(participant, id_event)
            if error:
                flash(error, "danger")
                return redirect(url_for('event.manage_event_participants', id_event=id_event))

        for participant in changes['participants']['removed']:
            error = database.delete_participates(participant, id_event)
            if error:
                flash(error, "danger")
                return redirect(url_for('event.manage_event_participants', id_event=id_event))

        flash("Modifications enregistrées avec succès!", "success")
        return redirect(url_for('event.manage_event_participants', id_event=id_event))

    if error:
        flash(error, "danger")
        return redirect(url_for('event.edit_event', id_event=id_event))
    return render_template('manage_event_participants.html', data=datas)