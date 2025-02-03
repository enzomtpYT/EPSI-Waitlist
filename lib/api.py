from lib import database, auth

def get_event_participants(id_event):
    event, error = database.get_event(id_event)
    participants, error = database.get_all_participants()
    candidates, error = database.get_all_candidates()
    alltags, error = database.get_all_tags()
    eventtag, error = database.get_event_tags(id_event)
    eventcandidates, error = database.get_event_candidates(id_event)
    eventparticipants, error = database.get_event_participant(id_event)

    eventcandidates = [dict(candidate) for candidate in eventcandidates]
    candidates = [dict(candidate) for candidate in candidates]
    eventparticipants = [dict(participant) for participant in eventparticipants]
    participants = [dict(participant) for participant in participants]

    event = dict(event)
    alltags = [dict(tag) for tag in alltags]

    for participant in participants:
        tags, error = database.get_participant_tags(participant["id_participant"])
        participant["tags"] = [tag["id_tag"] for tag in tags]
        if participant["id_participant"] in [participant["id_participant"] for participant in eventparticipants]:
            participant["attends"] = True
        else:
            participant["attends"] = False

    for candidate in candidates:
        tags, error = database.get_candidate_tags(candidate["id_candidate"])
        candidate["tags"] = [tag["id_tag"] for tag in tags]
        candidate["attends"] = False
        candidate["priority"] = 1
        for cand in eventcandidates:
            if candidate["id_candidate"] == cand["id_candidate"]:
                candidate["attends"] = True
                candidate["priority"] = cand["priority"]

    event["tags"] = [tag["id_tag"] for tag in eventtag]

    datas = {
        "event": dict(event),
        "participants": participants,
        "candidates": candidates,
        "tags": alltags
    }

    if error:
        return None, error

    return datas, None

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
            candidate_dict['interviews'] = interviews
        user_info, error = database.get_user(candidate['id_user'])
        if error:
            candidate_dict["username"] = ''
        else:
            candidate_dict["username"] = user_info["username"]
        candidates_with_tags.append(candidate_dict)
    
    return candidates_with_tags, None

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
    if type == "event":
        error = database.add_event(data)
    elif type == "participant":
        error = database.add_participant(data)
    elif type == "candidate":
        
        error = None
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
            if username is not None:
                error = database.auth_update_username(username, user_id)
                if error:
                    return error
            if password is not None:
                error = auth.update_user_pass(password, user_id)
                if error:
                    return error
        
    elif type == "employee":
        error = database.add_employee(data)
    elif type == "tag":
        error = database.add_tag(data)
    elif type == "interview":
        error = database.add_interview(data)
    else:
        return "Unknown type"
    return error

def update(type, data):
    if type == "event":
        error = database.update_event(data)
    elif type == "participant":
        error = database.update_participant(data)
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
            print(f'currenttags: {currenttags}\nnwetags: {newtags}')
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
        error = database.update_employee(data)
    elif type == "tag":
        error = database.update_tag(data)
    elif type == "interview":
        error = database.update_interview(data)
    else:
        return "Unknown type"
    return None