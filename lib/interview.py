import sqlite3
from lib.database import get_db_connection

# Interview functions

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

def get_candidate_from_event_participants_inverviews(id_event, id_participant):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        interviews = conn.execute('''
        SELECT Interview.id_interview, Candidate.lastname_candidate, Candidate.name_candidate, Candidate.id_candidate
        FROM Interview
        JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate
        WHERE Interview.id_event = ? AND Interview.id_participant = ?
        ''', (id_event, id_participant)).fetchall()
        return interviews, None
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