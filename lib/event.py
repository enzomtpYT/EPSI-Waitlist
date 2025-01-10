import sqlite3
from lib.database import get_db_connection, today

# Event functions

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

def get_event_interviews(id_event):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        event = conn.execute('SELECT * FROM Event WHERE id_event = ?', (id_event,)).fetchone()
        interviews = conn.execute('''
        SELECT Interview.id_interview, Participant.name_participant, Candidate.lastname_candidate, Candidate.name_candidate
        FROM Interview
        JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate
        JOIN Participant ON Interview.id_participant = Participant.id_participant
        JOIN Event ON Interview.id_event = Event.id_event
        WHERE Interview.id_event = ? AND Interview.happened = 1
        ''', (id_event,)).fetchall()
        return event, interviews, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

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