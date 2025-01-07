import sqlite3, datetime

def get_db_connection():
    try:
        conn = sqlite3.connect('BDDStage')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Erreure base de donnée: {e}")
        return None

today = datetime.date.today()

def get_event():
    conn = get_db_connection()
    if conn is None:
        return None, "Erreure base de donnée"
    try:
        events = conn.execute(f'SELECT id_event FROM Event WHERE date_event = \'{today}\'').fetchall()
        if events:
            return events[0]['id_event'], None
        else:
            return None, "Pas d'événement aujourd'hui"
    except sqlite3.Error as e:
        print(f"Erreure requete base de donnée: {e}")
        return None, "Erreure requete base de donnée"
    finally:
        conn.close()

def get_allevents():
    conn = get_db_connection()
    if conn is None:
        return None, "Erreure base de donnée"
    try:
        events = conn.execute(f'SELECT * FROM Event').fetchall()
        if events:
            return events, None
        else:
            return None, "Pas d'événement aujourd'hui"
    except sqlite3.Error as e:
        print(f"Erreure requete base de donnée: {e}")
        return None, "Erreure requete base de donnée"
    finally:
        conn.close()

def get_allcandidates():
    conn = get_db_connection()
    if conn is None:
        return None, "Erreure base de donnée"
    try:
        candidates = conn.execute(f'SELECT * FROM Candidate').fetchall()
        if candidates:
            return candidates, None
        else:
            return None, "Pas de candidat"
    except sqlite3.Error as e:
        print(f"Erreure requete base de donnée: {e}")
        return None, "Erreure requete base de donnée"
    finally:
        conn.close()

def get_event_candidats(todayevent):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreure base de donnée"
    try:
        candids = conn.execute(f'SELECT id_candidate FROM Participates WHERE id_event = \'{todayevent}\'').fetchall()
        candid = []
        for candidat in candids:
            candid.append(conn.execute(f'SELECT * FROM Candidate WHERE id_candidate = \'{candidat["id_candidate"]}\'').fetchall()[0])
    except sqlite3.Error as e:
        print(f"Erreure requete base de donnée: {e}")
        return None, "Erreure requete base de donnée"
    finally:
        conn.close()
    return candid, None

def delete_event(id_event):
    conn = get_db_connection()
    if conn is None:
        return "Erreure base de donnée"
    try:
        conn.execute("DELETE FROM Event WHERE id_event = ?", (id_event,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression de l'évenement: {e}")
        return "Erreur lors de la suppression de l'évenement"
    finally:
        conn.close()
    return None

def delete_candidate(id_candidate):
    conn = get_db_connection()
    if conn is None:
        return "Erreure base de donnée"
    try:
        conn.execute("DELETE FROM Candidate WHERE id_candidate = ?", (id_candidate,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression du candidat: {e}")
        return "Erreur lors de la suppression du candidat"
    finally:
        conn.close()
    return None

def get_event_intervenant(todayevent):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreure base de donnée"
    try:
        inters = conn.execute(f'SELECT id_participant FROM Attends WHERE id_event = \'{todayevent}\'').fetchall()
        inter = []
        for intervenant in inters:
            inter.append(conn.execute(f'SELECT * FROM Participant WHERE id_participant = \'{intervenant["id_participant"]}\'').fetchall()[0])
    except sqlite3.Error as e:
        print(f"Erreure requete base de donnée: {e}")
        return None, "Erreure requete base de donnée"
    finally:
        conn.close()
    return inter, None

def get_even_interview_candidate(todayevent, id_participant):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreure base de donnée"
    try:
        list = conn.execute(f'SELECT id_candidate FROM Interview WHERE id_event = \'{todayevent}\' AND id_participant = \'{id_participant}\'').fetchall()
        candid = []
        for candidat in list:
            cad = conn.execute(f'SELECT * FROM Candidate WHERE id_candidate = \'{candidat["id_candidate"]}\'').fetchall()
            for el in cad:
                candid.append(el)
        return candid, None
    except sqlite3.Error as e:
        print(f"Erreure requete base de donnée: {e}")
        return None, "Erreure requete base de donnée"
    finally:
        conn.close()

def get_candidate(candidate_id):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreure base de donnée"
    try:
        candidate = conn.execute('SELECT * FROM Candidate WHERE id_candidate = ?', (candidate_id,)).fetchone()
        return candidate, None
    except sqlite3.Error as e:
        print(f"Erreure requete base de donnée: {e}")
        return None, "Erreure requete base de donnée"
    finally:
        conn.close()

def get_event(event_id):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreure base de donnée"
    try:
        event = conn.execute('SELECT * FROM Event WHERE id_event = ?', (event_id,)).fetchone()
        return event, None
    except sqlite3.Error as e:
        print(f"Erreure requete base de donnée: {e}")
        return None, "Erreure requete base de donnée"
    finally:
        conn.close()

def get_participant(participant_id):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreure base de donnée"
    try:
        participant = conn.execute('SELECT * FROM Participant WHERE id_participant = ?', (participant_id,)).fetchone()
        return participant, None
    except sqlite3.Error as e:
        print(f"Erreure requete base de donnée: {e}")
        return None, "Erreure requete base de donnée"
    finally:
        conn.close()


def edit_candidate(lastname, name, email, id_candidate):
    conn = get_db_connection()
    if conn is None:
        return "Erreure base de donnée"
    try:
        conn.execute('UPDATE Candidate SET lastname_candidate = ?, name_candidate = ?, email_candidate = ? WHERE id_candidate = ?', (lastname, name, email, id_candidate))
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
        return "Erreure base de donnée"
    try:
        conn.execute('UPDATE Event SET name_event = ?, date_event = ? WHERE id_event = ?', (name, date, id_event))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour de l'évennement: {e}")
        return "Erreur lors de la mise à jour de l'évennement"
    finally:
        conn.close()
    return None