from lib import database, auth
from flask import jsonify, make_response
import datetime, random, threading
from collections.abc import MutableMapping
from fpdf import FPDF

class CacheManager(MutableMapping):
    def __init__(self):
        self.cache = { "events": {} }

    def __getitem__(self, key):
        value = self.cache[key]
        if isinstance(value, dict):
            value = CacheProxy(self, key, value)
        return value

    def __setitem__(self, key, value):
        self.cache[key] = value

    def __delitem__(self, key):
        del self.cache[key]

    def __iter__(self):
        return iter(self.cache)

    def __len__(self):
        return len(self.cache)

class CacheProxy(MutableMapping):
    def __init__(self, manager, parent_key, proxied_dict):
        self.manager = manager
        self.parent_key = parent_key
        self.proxied_dict = proxied_dict

    def __getitem__(self, key):
        value = self.proxied_dict[key]
        if isinstance(value, dict):
            value = CacheProxy(self.manager, self.parent_key, self.proxied_dict)
        return value

    def __setitem__(self, key, value):
        self.proxied_dict[key] = value
        self.manager[self.parent_key] = self.proxied_dict

    def __delitem__(self, key):
        del self.proxied_dict[key]
        self.manager[self.parent_key] = self.proxied_dict

    def __iter__(self):
        return iter(self.proxied_dict)

    def __len__(self):
        return len(self.proxied_dict)

    def to_dict(self):
        for k, v in self.proxied_dict.items():
            return v.to_dict() if isinstance(v, CacheProxy) else v

def timefixer(item):
    if isinstance(item, (datetime.time, datetime.datetime, datetime.date)):
        return item.strftime('%H:%M:%S' if isinstance(item, datetime.time) else '%Y-%m-%d %H:%M:%S' if isinstance(item, datetime.datetime) else '%Y-%m-%d')
    elif isinstance(item, dict):
        return {key: timefixer(value) for key, value in item.items()}
    elif isinstance(item, list):
        return [timefixer(element) for element in item]
    return item

cache = CacheManager()

def generate_pdf(id_event):
    event, error = database.get_event(id_event)
    if error:
        return None, error
    if not event:
        return None, "Aucun évenement avec cet id"

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
    if event.get('tags'):
        tag_names = ", ".join(tag.get('name_tag', 'N/A') for tag in event['tags'])
        pdf.cell(0, 10, f"Tags de l'événement : {tag_names}", 0, 1)
    pdf.ln(10)

    for interview in event.get('interviews', []):
        pdf.cell(0, 10, f"Intervenant : {interview.get('name_participant', 'N/A')}", 0, 1)
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
    return response, None

def updatecache_event(id):
    cached = cache["events"].get(str(id))
    if not cached:
        list, error = get_list(id, forced=True)
        if error:
            return
        cache["events"][str(id)] = list
        return
    cached = cached.to_dict()
    list, error = get_list(id, forced=True)
    if not error:
        if list != cached:
            cache["events"][str(id)] = list

def updatecache_all(id=None, type=None):
    types = [type] if type is not None else cache.keys()
    for type in types:
        ids = [id] if id is not None else cache[type].keys()
        for id in ids:
            if type == "events":
                threading.Thread(target=updatecache_event, args=(id,)).start()

def weighted_shuffle(arr, weights):
    """
    Mélange un tableau en utilisant des poids.
    Plus un élément a un poids élevé, plus il a de chances d'être proche de l'index 0.

    :param arr: Liste des éléments à mélanger.
    :param weights: Liste des poids associés aux éléments.
    :return: Liste mélangée selon les poids.
    """
    assert len(arr) == len(weights), "La taille des listes doit être identique."

    # Générer des clés pondérées et trier
    weighted_items = [(item, random.random() / weight) for item, weight in zip(arr, weights)]
    weighted_items.sort(key=lambda x: x[1])  # Trier selon la clé pondérée

    # Retourner uniquement les éléments dans le nouvel ordre
    return [item[0] for item in weighted_items]

def get_event_participants(id_event):
    datas, error = database.get_event_details(id_event)
    if error:
        return None, error
    return datas, None

def process_event_waitlist(datas):
    participants = datas.get("participants", [])

    for participant in participants:
        interviews, error = database.get_event_interview_candidate(datas["id_event"], participant["id_participant"])
        if error:
            return error

        old_ids = {str(interview["id_candidate"]) for interview in interviews}
        new_ids = {str(candidate) for candidate in participant["candidates"]}

        # Add new interviews
        for candidate in new_ids - old_ids:
            database.create_interview(datas["id_event"], participant["id_participant"], int(candidate))

        # Remove old interviews
        for interview in interviews:
            if str(interview["id_candidate"]) not in new_ids:
                database.delete_interview(interview["id_interview"])

    return None

def archive_schema(data):
    if data.get('target') is None:
        return "Missing target parameter"
    
    target = data.get('target')
    source = data.get('source')
    if source is None:
        error = database.archive_schema(target)
    else:
        error = database.archive_schema(target, source)
    if error:
        return error

def get_events():
    events, error = database.get_all_events()
    if error:
        return None, error

    return timefixer(events), None

def process_event_participants(datas):
    participants = datas.get("participants", [])
    candidates = datas.get("candidates", [])

    for participant in participants:
        if participant["attends"]:
            error = database.upsert_event_participates(datas["id_event"], participant["id_participant"])
        elif participant["attends"] is False:
            error = database.delete_participates(datas["id_event"], participant["id_participant"])
        if error:
            return error

    for candidate in candidates:
        if candidate["attends"]:
            error = database.upsert_event_attends(datas["id_event"], candidate["id_candidate"], candidate["priority"])
        elif candidate["attends"] is False:
            error = database.delete_attends(candidate["id_candidate"], datas["id_event"])
        if error:
            return error

    threading.Thread(target=updatecache_all, args=(datas["id_event"], "events")).start()

    return None

def api_interviews(session_token):
    interviews, error = database.get_user_past_interviews(session_token)
    events = {}
    for interview in interviews:
        interview_dict = dict(interview)
        if interview_dict['duration_interview'] is None:
            interview_dict['duration_interview'] = 0
        name = interview_dict['name_event']
        if events.get(name) is None:
            events[name] = {
                'name_event': name,
                'date_event': interview_dict['date_event'],
                'interviews': []
            }
        interview_dict.pop('name_event')
        interview_dict.pop('date_event')
        events[name]['interviews'].append(interview_dict)
    return events, None

def import_csv(datas):
    error = database.import_csv(datas)
    return error

def get_candidates():
    candidates, error = database.get_all_candidates()
    if error:
        return None, error

    candidates_with_tags = []
    for candidate in candidates:
        candidate_dict = dict(candidate)
        candidate_tags, error = database.get_candidate_tags(candidate['id_candidate'])
        if error:
            candidate_dict['tags'] = []
        else:
            candidate_dict['tags'] = candidate_tags
        interviews, error = database.get_candidate_interviews(candidate['id_candidate'])
        if error:
            candidate_dict['interviews'] = []
        else:
            for interview in interviews:
                if isinstance(interview['duration_interview'], datetime.time):
                    interview['duration_interview'] = interview['duration_interview'].strftime('%H:%M:%S')
            candidate_dict['interviews'] = interviews
        user_info, error = database.get_user(candidate['id_user'])
        if error:
            candidate_dict["username"] = ''
        else:
            candidate_dict["username"] = user_info["username"]
        candidates_with_tags.append(candidate_dict)

    return candidates_with_tags, None

def get_participants():
    participants, error = database.get_all_participants()
    if error:
        return None, error

    participants_with_tags = []
    for participant in participants:
        participant_dict = dict(participant)
        participant_tags, error = database.get_participant_tags(participant['id_participant'])
        if error:
            participant_dict['tags'] = []
        else:
            participant_dict['tags'] = participant_tags
        interviews, error = database.get_participant_interviews(participant['id_participant'])
        if error:
            participant_dict['interviews'] = []
        else:
            for interview in interviews:
                if isinstance(interview['duration_interview'], datetime.time):
                    interview['duration_interview'] = interview['duration_interview'].strftime('%H:%M:%S')
            participant_dict['interviews'] = interviews
        user_info, error = database.get_user(participant['id_user'])
        if error:
            participant_dict["username"] = ''
        else:
            participant_dict["username"] = user_info["username"]
        participants_with_tags.append(participant_dict)

    return participants_with_tags, None

def get_employees():
    employees, error = database.get_all_employees()
    if error:
        return None, error

    employees_return = []
    for employee in employees:
        employee_dict = dict(employee)
        interviews, error = database.get_employee_interviews(employee['id_employee'])
        if error:
            employee_dict['interviews'] = []
        else:
            for interview in interviews:
                if isinstance(interview['duration_interview'], datetime.time):
                    interview['duration_interview'] = interview['duration_interview'].strftime('%H:%M:%S')
            employee_dict['interviews'] = interviews
        user_info, error = database.get_user(employee['id_user'])
        if error:
            employee_dict["username"] = ''
        else:
            employee_dict["username"] = user_info["username"]
        employees_return.append(employee_dict)

    return employees_return, None

def move_interview(data):
    interview_id = data.get('id_interview')
    event_id = data.get('id_event')
    participant_name = data.get('name_participant')
    new_index = data.get('new_index')
    if not interview_id:
        return "Missing id_interview parameter"
    if not event_id:
        return "Missing id_event parameter"
    if not participant_name:
        return "Missing name_participant parameter"
    if new_index is None:
        return "Missing new_index parameter"
    
    cached = cache["events"].get(str(event_id))
    if cached is None:
        return "Aucun évenement avec cet id"
    event = cached.to_dict()
    if event.get("interviews") is None:
        return "Aucun entretien trouvé"
    if event["interviews"].get(participant_name) is None:
        return "Aucun participant trouvé"
    interviews = event["interviews"][participant_name]
    if new_index >= len(interviews):
        return "Index out of range"
    for i, interview in enumerate(interviews):
        if interview["id_interview"] == int(interview_id):
            interviews.insert(new_index, interviews.pop(i))
            break
    for i, interview in enumerate(interviews):
        print(f"Setting position {i} for interview {interview['id_interview']}")
        interview['position'] = i
    threading.Thread(target=updatecache_all, args=(event_id, "events")).start()

def get_list(id, forced=False):
    cached = cache["events"].get(str(id))
    if cached is not None and not forced:
        updatecache_all(id, "events")
        return cached.to_dict(), None
    event, error = database.get_event(id)
    event = dict(event)
    if error:
        return None, error
    elif event is None:
        return None, "Aucun évenement avec cet id"
    participants, error = database.get_event_participants(id)
    interviews = {}
    if participants:
        for participant in participants:
            order = []
            candidates, error = database.get_event_interview_candidate(id, participant['id_participant'], happened=False)
            for candidate in candidates:
                candidate = dict(candidate)
                if cached is not None:
                    ccached = cached.to_dict()
                    for cached_candidate in ccached["interviews"].get(participant['name_participant']):
                        if cached_candidate is not None and cached_candidate['id_candidate'] == candidate['id_candidate']:
                            pos = cached_candidate['position']
                            if len(order) <= pos:
                                order.extend([None] * (pos + 1 - len(order)))
                            order[pos] = candidate
                else:
                    order.append(candidate)
                    weights = [candidate["priority"] for candidate in order]
                    order = weighted_shuffle(order, weights)
            for candidatee in order:
                if candidatee == None:
                    order.remove(candidatee)
                    continue
                if candidatee['start_time_interview'] is not None:
                    order.remove(candidatee)
                    order.insert(0, candidatee)
            interviews[participant['name_participant']] = order
        
        hadswitch = True
        n = 0
        while hadswitch:
            hadswitch = False
            for part1 in interviews:
                if len(interviews[part1]) > 1:
                    id1 = interviews[part1][0]["id_candidate"]
                    for part2 in interviews:
                        if part1 != part2:
                            if len(interviews[part2]) > 1:
                                id2 = interviews[part2][0]["id_candidate"]
                                if id2 == id1:
                                    print('Detected same candidate in two interviews')
                                    r = 1
                                    if interviews[part1][0]["start_time_interview"] is None:
                                        if n > 0:
                                            r = min(int(random.gammavariate(2, 1)), len(interviews[part1]) - 1)
                                        interviews[part1][0], interviews[part1][r] = interviews[part1][r], interviews[part1][0]
                                    elif interviews[part2][0]["start_time_interview"] is None:
                                        if n > 0:
                                            r = min(int(random.gammavariate(2, 1)), len(interviews[part2]) - 1)
                                        interviews[part2][0], interviews[part2][r] = interviews[part2][r], interviews[part2][0]
                                    hadswitch = True
            n += 1
            if n > 10:
                break
        for interview in interviews.values():
            for i, candidate in enumerate(interview):
                candidate['position'] = i
        event["interviews"] = interviews
    if not forced:
        cache["events"][str(id)] = event
    return timefixer(event), None

def start_interview(data):
    start_time = None
    if data.get('start_time') is not None:
        try:
            start_time = datetime.datetime.strptime(data.get('start_time'), "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            return jsonify({"error": "Invalid start_time format"}), 400

    id_interview = data.get('id_interview')
    if not id_interview:
        return jsonify({"error": "Missing id_interview parameter"}), 400

    updated_id, error = database.editstart_interview(id_interview, start_time)

    updatecache_all(data.get('id_event'), "events")

    if error:
        return jsonify({"error": error}), 400

def end_interview(data):
    if data.get('id_interview') is not None:
        interview_id = data.get('id_interview')
        error = database.end_interview(interview_id, status=True)
        if error:
            return jsonify({"error": error}), 400
        event_cache = cache["events"].get(str(data.get('id_event')))
        if event_cache and "interviews" in event_cache:
            for interviews in event_cache["interviews"].values():
                for interview in interviews:
                    if interview["id_interview"] == interview_id:
                        interviews.remove(interview)
        updatecache_all(data.get('id_event'), "events")

def skip_candidate(event_id, name_participant):
    """" Skip le candidat actuel et le met en 2 ème position dans le cache """

    event_id = str(event_id)
    if cache["events"].get(event_id) is None:
        return "Aucun évenement avec cet id"

    event = cache["events"][event_id]
    event = event.to_dict()
    if event.get("interviews") is None:
        return "Aucun entretien trouvé"

    if event["interviews"].get(name_participant) is None:
        return "Aucun participant trouvé"

    interviews = event["interviews"][name_participant]
    if len(interviews) < 2:
        return "Pas assez de candidats"

    interviews[0], interviews[1] = interviews[1], interviews[0]

def delete(type, id):
    if type == "event":
        error = database.delete_event(id)
    elif type == "participant":
        error = database.delete_participant(id)
    elif type == "candidate":
        error = database.delete_candidate(id)
    elif type == "employee":
        error = database.delete_employee(id)
    elif type == "tag":
        error = database.delete_tag(id)
    elif type == "interview":
        error = database.delete_interview(id)
    else:
        return "Unknown type"
    return error

def add(type, data):
    error = None
    
    if type == "event":
        
        name_event = data.get("name_event")
        start_time_event = data.get("start_time_event")
        end_time_event = data.get("end_time_event")
        date_event = data.get("date_event")
        selected_tags = data.get("tags")
        if name_event is None or start_time_event is None or end_time_event is None or date_event is None:
            return "Champs manquants"
        event_id, error = database.create_event(name_event, date_event, start_time_event=start_time_event, end_time_event=end_time_event, tags=selected_tags)
        return error
                
    elif type == "participant":

        name_participant = data.get("name_participant")
        email_participant = data.get("email_participant")
        selected_tags = data.get("tags")
        if name_participant is None or email_participant is None:
            return "Champs manquants"
        participant_id, user_id, error = database.create_participant(name_participant, email_participant)
        if error is None:
            for tag in selected_tags:
                database.add_tag_to_participant(participant_id, tag["id_tag"])
            username = data.get("username")
            password = data.get("password")
            if username not in (None, ''):
                error = database.auth_update_username(username, user_id)
                if error:
                    return error
            if password not in (None, ''):
                error = auth.update_user_pass(password, user_id)
                if error:
                    return error

    elif type == "candidate":

        lastname_candidate = data.get("lastname_candidate")
        name_candidate = data.get("name_candidate")
        email_candidate = data.get("email_candidate")
        selected_tags = data.get("tags")
        if lastname_candidate is None or name_candidate is None or email_candidate is None:
            return "Champs manquants"
        candidate_id, user_id, error = database.create_candidate(lastname_candidate, name_candidate, email_candidate)
        if error is None:
            for tag in selected_tags:
                database.add_tag_to_candidate(candidate_id, tag["id_tag"])
            username = data.get("username")
            password = data.get("password")
            if username not in (None, ''):
                error = database.auth_update_username(username, user_id)
                if error:
                    return error
            if password not in (None, ''):
                error = auth.update_user_pass(password, user_id)
                if error:
                    return error

    elif type == "employee":

        lastname_employee = data.get("lastname_employee")
        name_employee = data.get("name_employee")
        email_employee = data.get("email_employee")
        role = data.get("name_role")
        if lastname_employee is None or name_employee is None or email_employee is None or role is None:
            return "Champs manquants"
        employee_id, user_id, error = database.create_employee(lastname_employee, name_employee, email_employee, role)
        if error is None:
            username = data.get("username")
            password = data.get("password")
            if username not in (None, ''):
                error = database.auth_update_username(username, user_id)
                if error:
                    return error
            if password not in (None, ''):
                error = auth.update_user_pass(password, user_id)
                if error:
                    return error

    elif type == "tag":
        error = database.add_tag(data)
    elif type == "interview":
        error = database.add_interview(data)
    else:
        return "Unknown type"
    return error

def update(type, data):
    if type == "event":
        
        id_event = data.get("id_event")
        name_event = data.get("name_event")
        start_time_event = data.get("start_time_event")
        end_time_event = data.get("end_time_event")
        date_event = data.get("date_event")
        newtags = data.get("tags")
        currenttags, error = database.get_event_tags(id_event)
        currenttags = [dict(tag) for tag in currenttags]
        if name_event is None or start_time_event is None or end_time_event is None or date_event is None:
            return "Champs manquants"
        error = database.edit_event(name_event, date_event, id_event, start_time_event=start_time_event, end_time_event=end_time_event)
        if error:
            return error
        if newtags is not None:
            for otag in currenttags:
                if otag not in newtags:
                    database.remove_tag_from_event(id_event, otag['id_tag'])
            for ntag in newtags:
                if ntag not in currenttags:
                    database.add_tag_to_event(id_event, ntag['id_tag'])
        
    elif type == "participant":

        id_participant = data.get("id_participant")
        name_participant = data.get("name_participant")
        email_participant = data.get("email_participant")
        newtags = data.get("tags")
        currenttags, error = database.get_participant_tags(id_participant)
        currenttags = [dict(tag) for tag in currenttags]
        if name_participant is None or email_participant is None:
            return "Champs manquants"
        error = database.edit_participant(name_participant, email_participant, id_participant)
        if error:
            return error
        if newtags is not None:
            for otag in currenttags:
                if otag not in newtags:
                    database.remove_tag_from_participant(id_participant, otag['id_tag'])
            for ntag in newtags:
                if ntag not in currenttags:
                    database.add_tag_to_participant(id_participant, ntag['id_tag'])
        id_user = data.get("id_user")
        username = data.get("username")
        password = data.get("password")
        if error is None:
            if username is not None:
                error = database.auth_update_username(username, id_user)
                if error:
                    return error
            if password is not None:
                error = auth.update_user_pass(password, id_user)
                if error:
                    return error

    elif type == "candidate":

        id_candidate = data.get("id_candidate")
        lastname_candidate = data.get("lastname_candidate")
        name_candidate = data.get("name_candidate")
        email_candidate = data.get("email_candidate")
        newtags = data.get("tags")
        currenttags, error = database.get_candidate_tags(id_candidate)
        currenttags = [dict(tag) for tag in currenttags]
        if lastname_candidate is None or name_candidate is None or email_candidate is None:
            return "Champs manquants"
        error = database.edit_candidate(lastname_candidate, name_candidate, email_candidate, id_candidate)
        if error:
            return error
        if newtags is not None:
            for otag in currenttags:
                if otag not in newtags:
                    database.remove_tag_from_candidate(id_candidate, otag['id_tag'])
            for ntag in newtags:
                if ntag not in currenttags:
                    database.add_tag_to_candidate(id_candidate, ntag['id_tag'])
        id_user = data.get("id_user")
        username = data.get("username")
        password = data.get("password")
        if error is None:
            if username is not None:
                error = database.auth_update_username(username, id_user)
                if error:
                    return error
            if password is not None:
                error = auth.update_user_pass(password, id_user)
                if error:
                    return error

    elif type == "employee":

        id_employee = data.get('id_employee')
        lastname_employee = data.get('lastname_employee')
        name_employee = data.get('name_employee')
        email_employee = data.get('email_employee')
        role = data.get('name_role')
        if id_employee is None or lastname_employee is None or name_employee is None or email_employee is None or role is None:
            return "Champs manquants"
        error = database.edit_employee(lastname_employee, name_employee, email_employee, role, id_employee)

        id_user = data.get("id_user")
        username = data.get("username")
        password = data.get("password")
        if error is None:
            if username is not None:
                error = database.auth_update_username(username, id_user)
                if error:
                    return error
            if password is not None:
                error = auth.update_user_pass(password, id_user)
                if error:
                    return error

    elif type == "tag":
        error = database.update_tag(data)
    elif type == "interview":
        error = database.update_interview(data)
    else:
        return "Unknown type"
    return None