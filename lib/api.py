from lib import database

def get_event_participants(id_event):
    event, error = database.get_event(id_event)
    participants, error = database.get_all_participants()
    candidates, error = database.get_all_candidates()
    alltags, error = database.get_all_tags()
    eventtag, error = database.get_event_tags(id_event)
    
    event = dict(event)
    participants = [dict(participant) for participant in participants]
    candidates = [dict(candidate) for candidate in candidates]
    alltags = [dict(tag) for tag in alltags]
    
    for participant in participants:
        tags, error = database.get_participant_tags(participant["id_participant"])
        participant["tags"] = [tag["id_tag"] for tag in tags]
    for candidate in candidates:
        tags, error = database.get_candidate_tags(candidate["id_candidate"])
        candidate["tags"] = [tag["id_tag"] for tag in tags]
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