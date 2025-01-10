import sqlite3
from lib.database import get_db_connection

#Tag functions

def create_tag(name):
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute('INSERT INTO Tag (name_tag) VALUES (?)', (name,))
        conn.commit()
        return None
    except sqlite3.Error as e:
        print(f"Erreur lors de la création du tag: {e}")
        return "Erreur lors de la création du tag"
    finally:
        conn.close()

def get_all_tags():
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        tags = conn.execute('SELECT * FROM Tag').fetchall()
        if tags:
            return tags, None
        else:
            return [], "Pas de tag"
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return [], "Erreur requête base de données"
    finally:
        conn.close()

def get_tag(tag_id):
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        tag = conn.execute('SELECT * FROM Tag WHERE id_tag = ?', (tag_id,)).fetchone()
        return tag, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def edit_tag(name, id_tag):
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute('UPDATE Tag SET name_tag = ? WHERE id_tag = ?', (name, id_tag))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour du tag: {e}")
        return "Erreur lors de la mise à jour du tag"
    finally:
        conn.close()
    return None

def delete_tag(id_tag):
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute("DELETE FROM Tag WHERE id_tag = ?", (id_tag,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression du candidat: {e}")
        return "Erreur lors de la suppression du candidat"
    finally:
        conn.close()
    return None

def get_candidate_tags(id_candidate):
    conn = get_db_connection()
    try:
        tags = conn.execute('''
        SELECT Tag.id_tag, Tag.name_tag
        FROM Tag
        JOIN Candidate_tag ON Tag.id_tag = Candidate_tag.id_tag
        WHERE Candidate_tag.id_candidate = ?
        ''', (id_candidate,)).fetchall()
        conn.close()
        return tags, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def add_tag_to_candidate(id_candidate, id_tag):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO Candidate_tag (id_candidate, id_tag) VALUES (?, ?)', (id_candidate, id_tag))
        conn.commit()
        conn.close()
        return None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return "Erreur requête base de données"
    finally:
        conn.close()

def remove_tag_from_candidate(id_candidate, id_tag):
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM Candidate_tag WHERE id_candidate = ? AND id_tag = ?', (id_candidate, id_tag))
        conn.commit()
        conn.close()
        return None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return "Erreur requête base de données"
    finally:
        conn.close()

def get_participant_tags(id_participant):
    conn = get_db_connection()
    try:
        tags = conn.execute('''
        SELECT Tag.id_tag, Tag.name_tag
        FROM Tag
        JOIN Participant_tag ON Tag.id_tag = Participant_tag.id_tag
        WHERE Participant_tag.id_participant = ?
        ''', (id_participant,)).fetchall()
        conn.close()
        return tags, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def add_tag_to_participant(id_participant, id_tag):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO Participant_tag (id_participant, id_tag) VALUES (?, ?)', (id_participant, id_tag))
        conn.commit()
        conn.close()
        return None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return "Erreur requête base de données"
    finally:
        conn.close()

def remove_tag_from_participant(id_participant, id_tag):
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM Participant_tag WHERE id_participant = ? AND id_tag = ?', (id_participant, id_tag))
        conn.commit()
        conn.close()
        return None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return "Erreur requête base de données"
    finally:
        conn.close()

def get_event_tags(id_event):
    conn = get_db_connection()
    try:
        tags = conn.execute('''
        SELECT Tag.*
        FROM Tag
        JOIN Event_tag ON Tag.id_tag = Event_tag.id_tag
        WHERE Event_tag.id_event = ?
        ''', (id_event,)).fetchall()
        conn.close()
        return tags, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def add_tag_to_event(id_event, id_tag):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO Event_tag (id_event, id_tag) VALUES (?, ?)', (id_event, id_tag))
        conn.commit()
        conn.close()
        return None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return "Erreur requête base de données"
    finally:
        conn.close()

def remove_tag_from_event(id_event, id_tag):
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM Event_tag WHERE id_event = ? AND id_tag = ?', (id_event, id_tag))
        conn.commit()
        conn.close()
        return None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return "Erreur requête base de données"
    finally:
        conn.close()