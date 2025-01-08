import sqlite3, datetime

def get_db_connection():
    try:
        conn = sqlite3.connect('BDDStage')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Erreur base de données: {e}")
        return None

today = datetime.date.today()

def get_today_events():
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        events = conn.execute(f'SELECT id_event FROM Event WHERE date_event = \'{today}\'').fetchall()
        if events:
            return events[0]['id_event'], None
        else:
            return None, "Pas d'événement aujourd'hui"
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_all_events():
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        events = conn.execute(f'SELECT * FROM Event').fetchall()
        if events:
            return events, None
        else:
            return None, "Pas d'événement aujourd'hui"
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_all_candidates():
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        candidates = conn.execute(f'SELECT * FROM Candidate').fetchall()
        if candidates:
            return candidates, None
        else:
            return None, "Pas de candidat"
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_all_participants():
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        participants = conn.execute(f'SELECT * FROM Participant').fetchall()
        if participants:
            return participants, None
        else:
            return None, "Pas d'intervenant"
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_event_candidates(todayevent):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        candids = conn.execute(f'SELECT id_candidate FROM Participates WHERE id_event = \'{todayevent}\'').fetchall()
        candid = []
        for candidat in candids:
            candid.append(conn.execute(f'SELECT * FROM Candidate WHERE id_candidate = \'{candidat["id_candidate"]}\'').fetchall()[0])
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()
    return candid, None

def delete_event(id_event):
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute("DELETE FROM Event WHERE id_event = ?", (id_event,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression de l'événement: {e}")
        return "Erreur lors de la suppression de l'événement"
    finally:
        conn.close()
    return None

def delete_candidate(id_candidate):
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute("DELETE FROM Candidate WHERE id_candidate = ?", (id_candidate,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression du candidat: {e}")
        return "Erreur lors de la suppression du candidat"
    finally:
        conn.close()
    return None

def delete_participant(id_participant):
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute("DELETE FROM Participant WHERE id_participant = ?", (id_participant,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression de l'intervenant: {e}")
        return "Erreur lors de la suppression de l'intervenant"
    finally:
        conn.close()
    return None

def get_event_participant(todayevent):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        inters = conn.execute(f'SELECT id_participant FROM Attends WHERE id_event = \'{todayevent}\'').fetchall()
        inter = []
        for intervenant in inters:
            inter.append(conn.execute(f'SELECT * FROM Participant WHERE id_participant = \'{intervenant["id_participant"]}\'').fetchall()[0])
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()
    return inter, None

def get_event_interview_candidate(todayevent, id_participant):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        list = conn.execute(f'SELECT id_candidate FROM Interview WHERE id_event = \'{todayevent}\' AND id_participant = \'{id_participant}\' AND happened = \'0\'').fetchall()
        candid = []
        for candidat in list:
            cad = conn.execute(f'SELECT * FROM Candidate WHERE id_candidate = \'{candidat["id_candidate"]}\'').fetchall()
            for el in cad:
                candid.append(el)
        return candid, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_candidate(candidate_id):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        candidate = conn.execute('SELECT * FROM Candidate WHERE id_candidate = ?', (candidate_id,)).fetchone()
        return candidate, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_event(event_id):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        event = conn.execute('SELECT * FROM Event WHERE id_event = ?', (event_id,)).fetchone()
        return event, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_participant(participant_id):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        participant = conn.execute('SELECT * FROM Participant WHERE id_participant = ?', (participant_id,)).fetchone()
        return participant, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()


def edit_candidate(lastname, name, email, year, candidate_class, id_candidate):
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute('UPDATE Candidate SET lastname_candidate = ?, name_candidate = ?, email_candidate = ?, year_candidate = ?, class_candidate = ? WHERE id_candidate = ?', (lastname, name, email, year, candidate_class, id_candidate))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour du candidat: {e}")
        return "Erreur lors de la mise à jour du candidat"
    finally:
        conn.close()
    return None

def edit_event(name, date, id_event):
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute('UPDATE Event SET name_event = ?, date_event = ? WHERE id_event = ?', (name, date, id_event))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour de l'événnement: {e}")
        return "Erreur lors de la mise à jour de l'événnement"
    finally:
        conn.close()
    return None

def edit_participant(name, email, id_participant):
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute('UPDATE Participant SET name_participant = ?, email_participant = ? WHERE id_participant = ?', (name, email, id_participant))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour de l'intervenant: {e}")
        return "Erreur lors de la mise à jour de l'intervenant"
    finally:
        conn.close()
    return None

def create_interview(id_event, id_participant, id_candidate):
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute('INSERT INTO Interview (id_event, id_participant, id_candidate, happened) VALUES (?, ?, ?, 0)', (id_event, id_participant, id_candidate))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la création de l'interview: {e}")
        return "Erreur lors de la création de l'interview"
    finally:
        conn.close()
    return None

def get_event_interviews(id_event):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        interviews = conn.execute('SELECT Interview.id_interview, Participant.name_participant, Candidate.lastname_candidate, Candidate.name_candidate FROM Interview JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate JOIN Participant ON Interview.id_participant = Participant.id_participant JOIN Event ON Interview.id_event = Event.id_event WHERE Interview.id_event = ?', (id_event,)).fetchall()
        return interviews, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_participant_interviews(id_participant):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        interviews = conn.execute('SELECT Interview.id_interview, Event.name_event, Candidate.lastname_candidate, Candidate.name_candidate FROM Interview JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate JOIN Participant ON Interview.id_participant = Participant.id_participant JOIN Event ON Interview.id_event = Event.id_event WHERE Interview.id_participant = ?', (id_participant,)).fetchall()
        return interviews, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_candidate_interviews(id_candidate):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        interviews = conn.execute('SELECT Interview.id_interview, Event.name_event, Participant.name_participant FROM Interview JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate JOIN Participant ON Interview.id_participant = Participant.id_participant JOIN Event ON Interview.id_event = Event.id_event WHERE Interview.id_candidate = ?', (id_candidate,)).fetchall()
        return interviews, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_interview(id_interview):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        interview = conn.execute('SELECT * FROM Interview WHERE id_interview = ?', (id_interview,)).fetchone()
        return interview, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def edit_interview(id_interview, happened):
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute('UPDATE Interview SET happened = ? WHERE id_interview = ?', (happened, id_interview))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour de l'interview: {e}")
        return "Erreur lors de la mise à jour de l'interview"
    finally:
        conn.close()
    return None

def delete_interview(id_interview):
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute("DELETE FROM Interview WHERE id_interview = ?", (id_interview,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression de l'interview: {e}")
        return "Erreur lors de la suppression de l'interview"
    finally:
        conn.close()
    return None

def create_event(name, date):
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute('INSERT INTO Event (name_event, date_event) VALUES (?, ?)', (name, date))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la création de l'événement: {e}")
        return "Erreur lors de la création de l'événement"
    finally:
        conn.close()
    return None