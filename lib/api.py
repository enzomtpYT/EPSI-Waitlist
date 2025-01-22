from lib import database

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