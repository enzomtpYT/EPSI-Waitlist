import sqlite3
from lib.database import get_db_connection

# Candidate functions

def create_candidate(lastname, name, email):
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute('INSERT INTO Candidate (lastname_candidate, name_candidate, email_candidate) VALUES (?, ?, ?)', (lastname, name, email))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la création du candidat: {e}")
        return "Erreur lors de la création du candidat"
    finally:
        conn.close()
    return None

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

def edit_candidate(lastname, name, email, id_candidate):
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute('UPDATE Candidate SET lastname_candidate = ?, name_candidate = ?, email_candidate = ? WHERE id_candidate = ?', (lastname, name, email, id_candidate))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour du candidat: {e}")
        return "Erreur lors de la mise à jour du candidat"
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

def get_candidate_interviews(id_candidate):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        interviews = conn.execute('''
        SELECT Interview.id_interview, Event.name_event, Event.date_event, Participant.name_participant
        FROM Interview
        JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate
        JOIN Participant ON Interview.id_participant = Participant.id_participant
        JOIN Event ON Interview.id_event = Event.id_event
        WHERE Interview.id_candidate = ? AND Interview.happened = 1
        ''', (id_candidate,)).fetchall()
        return interviews, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()