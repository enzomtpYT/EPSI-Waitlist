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
    eventparticipants = [dict(participant) for participant in eventparticipants]
    
    event = dict(event)
    participants = [dict(participant) for participant in participants]
    candidates = [dict(candidate) for candidate in candidates]
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
        if candidate["id_candidate"] in [candidate["id_candidate"] for candidate in eventcandidates]:
            candidate["attends"] = True
        else:
            candidate["attends"] = False
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