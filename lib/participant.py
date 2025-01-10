import sqlite3
from lib.database import get_db_connection

# Participant functions

def create_participant(name, email):
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute('INSERT INTO Participant (name_participant, email_participant) VALUES (?, ?)', (name, email))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la création de l'intervenant: {e}")
        return "Erreur lors de la création de l'intervenant"
    finally:
        conn.close()
    return None

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

def get_participant_interviews(id_participant):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        interviews = conn.execute('''
        SELECT Interview.id_interview, Event.name_event, Event.date_event, Candidate.lastname_candidate, Candidate.name_candidate
        FROM Interview
        JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate
        JOIN Participant ON Interview.id_participant = Participant.id_participant
        JOIN Event ON Interview.id_event = Event.id_event
        WHERE Interview.id_participant = ? AND Interview.happened = 1
        ''', (id_participant,)).fetchall()
        return interviews, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()