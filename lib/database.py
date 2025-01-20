import sqlite3, datetime

def get_db_connection():
    """
    Établit une connexion à la base de données SQLite.

    Returns:
        sqlite3.Connection: L'objet de connexion à la base de données.
        None: Si une erreur survient lors de la connexion.
    """
    try:
        conn = sqlite3.connect('BDDStage')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Erreur base de données: {e}")
        return None

today = datetime.date.today()

# Event functions

def create_event(name, date):
    """
    Crée un nouvel événement dans la base de données.

    Args:
        name (str): Le nom de l'événement.
        date (str): La date de l'événement.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Event (name_event, date_event) VALUES (?, ?)', (name, date))
        event_id = cursor.lastrowid
        conn.commit()
        return event_id, None
    except sqlite3.Error as e:
        print(f"Erreur lors de la création de l'événement: {e}")
        return None, "Erreur lors de la création de l'événement"
    finally:
        conn.close()

def get_all_events():
    """
    Récupère tous les événements de la base de données.

    Returns:
        list: Une liste de dictionnaires représentant les événements.
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
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
    """
    Récupère un événement de la base de données en utilisant son identifiant.

    Args:
        event_id (int): L'identifiant de l'événement.

    Returns:
        dict: Un dictionnaire représentant l'événement.
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
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
    """
    Met à jour un événement dans la base de données.

    Args:
        name (str): Le nom de l'événement.
        date (str): La date de l'événement.
        id_event (int): L'identifiant de l'événement.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
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
    """
    Supprime un événement de la base de données en utilisant son identifiant.

    Args:
        id_event (int): L'identifiant de l'événement.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
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
    """
    Récupère les interviews associées à un événement.

    Args:
        id_event (int): L'identifiant de l'événement.

    Returns:
        tuple: Un tuple contenant l'événement, les interviews et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        event = conn.execute('SELECT * FROM Event WHERE id_event = ?', (id_event,)).fetchone()
        interviews = conn.execute('''
        SELECT Interview.id_interview, Participant.name_participant, Candidate.lastname_candidate, Candidate.name_candidate, Interview.feedback_participant, Interview.feedback_candidate, Interview.duration_interview
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
    """
    Récupère les événements prévus pour aujourd'hui.

    Returns:
        tuple: Un tuple contenant l'identifiant de l'événement et un message d'erreur si une erreur est survenue.
    """
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

def get_event_candidates(id):
    """
    Récupère les candidats associés à un événement.

    Args:
        todayevent (int): L'identifiant de l'événement.

    Returns:
        tuple: Un tuple contenant une liste de candidats et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        candidates = conn.execute('''
        SELECT Candidate.*, Participates.priority
        FROM Candidate
        JOIN Participates ON Candidate.id_candidate = Participates.id_candidate
        WHERE Participates.id_event = ?
        ''', (id,)).fetchall()
        return candidates, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_event_participant(id):
    """
    Récupère les participants associés à un événement.

    Args:
        todayevent (int): L'identifiant de l'événement.

    Returns:
        tuple: Un tuple contenant une liste de participants et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        inter = conn.execute('''
        SELECT Participant.*
        FROM Participant
        JOIN Attends ON Participant.id_participant = Attends.id_participant
        WHERE Attends.id_event = ?
        ''', (id,)).fetchall()
        return inter, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_event_interview_candidate(todayevent, id_participant):
    """
    Récupère les candidats associés aux interviews d'un participant pour un événement.

    Args:
        todayevent (int): L'identifiant de l'événement.
        id_participant (int): L'identifiant du participant.

    Returns:
        tuple: Un tuple contenant une liste de candidats et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        list = conn.execute(f'SELECT Interview.id_candidate, Candidate.lastname_candidate, Candidate.name_candidate, Candidate.email_candidate, Interview.id_interview FROM Interview JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate WHERE id_event = \'{todayevent}\' AND id_participant = \'{id_participant}\' AND happened = \'0\'').fetchall()
        candid = []
        for el in list:
            candid.append(el)
        return candid, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

# Candidate functions

def create_candidate(lastname, name, email):
    """
    Crée un nouveau candidat dans la base de données.

    Args:
        lastname (str): Le nom de famille du candidat.
        name (str): Le prénom du candidat.
        email (str): L'adresse email du candidat.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor = conn.cursor()

        # Insère l'utilisateur dans la table User
        cursor.execute('INSERT INTO User (username) VALUES (?)', (email,))
        user_id = cursor.lastrowid
        print(f"User created with ID: {user_id}")

        # Insere le candidat dans la base de données
        cursor.execute('INSERT INTO Candidate (lastname_candidate, name_candidate, email_candidate, id_user) VALUES (?, ?, ?, ?)', (lastname, name, email, user_id))
        candidate_id = cursor.lastrowid
        print(f"Candidate created with ID: {candidate_id}")

        # Sauvegarde les modifications
        conn.commit()
        return candidate_id, None
    except sqlite3.Error as e:
        print(f"Erreur lors de la création du candidat: {e}")
        return None, "Erreur lors de la création du candidat"
    finally:
        # Fermes la connexion à la base de données
        conn.close()

def get_candidate_email(id_candidate):
    """
    Récupère l'adresse email d'un candidat en utilisant son identifiant.

    Args:
        id_candidate (int): L'identifiant du candidat.

    Returns:
        str: L'adresse email du candidat.
    """
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        candidate = conn.execute('SELECT email_candidate FROM Candidate WHERE id_candidate = ?', (id_candidate,)).fetchone()
        return candidate['email_candidate']
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None
    finally:
        conn.close()

def get_all_candidates():
    """
    Récupère tous les candidats de la base de données.

    Returns:
        tuple: Un tuple contenant une liste de candidats et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"

    try:
        # Renvoie tous les candidats de la base de données
        candidates = conn.execute('SELECT * FROM Candidate').fetchall()

        if candidates:
            return candidates, None
        else:
            return None, "Pas de candidat"

    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"

    finally:
        # Fermes la connexion à la base de données
        conn.close()

def get_candidate(candidate_id):
    """
    Récupère un candidat de la base de données en utilisant son identifiant.

    Args:
        candidate_id (int): L'identifiant du candidat.

    Returns:
        tuple: Un tuple contenant le candidat et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        # Si la connexion échoue, renvoie une erreur
        return None, "Erreur base de données"
    try:
        # Exécute la requête pour récupérer le candidat
        candidate = conn.execute('SELECT * FROM Candidate WHERE id_candidate = ?', (candidate_id,)).fetchone()
        return candidate, None
    except sqlite3.Error as e:
        # Gère les erreurs de requête SQL
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        # Ferme la connexion à la base de données
        conn.close()

def edit_candidate(lastname, name, email, id_candidate):
    """
    Met à jour un candidat dans la base de données.

    Args:
        lastname (str): Le nom de famille du candidat.
        name (str): Le prénom du candidat.
        email (str): L'adresse email du candidat.
        id_candidate (int): L'identifiant du candidat.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"

    try:
        # Met à jour le candidat dans la base de données
        conn.execute('UPDATE Candidate SET lastname_candidate = ?, name_candidate = ?, email_candidate = ? WHERE id_candidate = ?', (lastname, name, email, id_candidate))
        # Sauvegarde les modifications
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour du candidat: {e}")
        return "Erreur lors de la mise à jour du candidat"
    finally:
        # Fermes la connexion à la base de données
        conn.close()
    return None

def delete_candidate(id_candidate):
    """
    Supprime un candidat de la base de données en utilisant son identifiant.

    Args:
        id_candidate (int): L'identifiant du candidat.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        # Si la connexion échoue, renvoie une erreur
        return "Erreur base de données"
    try:
        # Exécute la requête pour supprimer le candidat
        conn.execute("DELETE FROM Candidate WHERE id_candidate = ?", (id_candidate,))
        # Sauvegarde les modifications
        conn.commit()
    except sqlite3.Error as e:
        # Gère les erreurs de requête SQL
        print(f"Erreur lors de la suppression du candidat: {e}")
        return "Erreur lors de la suppression du candidat"
    finally:
        # Ferme la connexion à la base de données
        conn.close()
    return None

def get_candidate_interviews(id_candidate):
    """
    Récupère les interviews associées à un candidat.

    Args:
        id_candidate (int): L'identifiant du candidat.

    Returns:
        tuple: Un tuple contenant une liste d'interviews et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"

    try:
        # Renvoie les entretiens du candidat
        interviews = conn.execute('''
        SELECT Interview.id_interview, Event.name_event, Event.date_event, Participant.name_participant, Interview.feedback_candidate, Interview.feedback_participant, Interview.duration_interview
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
        # Ferme la connexion à la base de données
        conn.close()

def get_last_added_candidate():
    """
    Récupère le dernier candidat ajouté à la base de données.

    Returns:
        tuple: Un tuple contenant le candidat et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        # Si la connexion échoue, renvoie une erreur
        return None, "Erreur base de données"
    try:
        # Renvoie le dernier candidat ajouté
        candidate = conn.execute('SELECT * FROM Candidate ORDER BY id_candidate DESC LIMIT 1').fetchone()
        return candidate, None
    except sqlite3.Error as e:
        # Gère les erreurs de requête SQL
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        # Ferme la connexion à la base de données
        conn.close()

def remove_candidate_from_all_interviews_for_event(id_event, id_candidate):
    """
    Supprime un candidat de tous les entretiens associés à un événement.

    Args:
        id_event (int): L'identifiant de l'événement.
        id_candidate (int): L'identifiant du candidat.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        # Si la connexion échoue, renvoie une erreur
        return "Erreur base de données"
    try:
        # Exécute la requête pour supprimer le candidat de tous les entretiens associés à l'événement
        conn.execute("DELETE FROM Interview WHERE id_event = ? AND id_candidate = ?", (id_event, id_candidate))
        # Sauvegarde les modifications
        conn.commit()
    except sqlite3.Error as e:
        # Gère les erreurs de requête SQL
        print(f"Erreur lors de la suppression du candidat: {e}")
        return "Erreur lors de la suppression du candidat"
    finally:
        # Ferme la connexion à la base de données
        conn.close()
    return None

def add_candidate_to_event(id_event, id_candidate):
    """
    Ajoute un candidat à un événement.

    Args:
        id_event (int): L'identifiant de l'événement.
        id_candidate (int): L'identifiant du candidat.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        # Si la connexion échoue, renvoie une erreur
        return "Erreur base de données"
    try:
        # Exécute la requête pour ajouter le candidat à l'événement
        conn.execute('INSERT INTO Participates (id_event, id_candidate) VALUES (?, ?)', (id_event, id_candidate))
        # Sauvegarde les modifications
        conn.commit()
    except sqlite3.Error as e:
        # Gère les erreurs de requête SQL
        print(f"Erreur lors de l'ajout du candidat à l'événement: {e}")
        return "Erreur lors de l'ajout du candidat à l'événement"
    finally:
        # Ferme la connexion à la base de données
        conn.close()
    return None

def delete_candidate_from_event(id_event, id_candidate):
    """
    Supprime un candidat d'un événement.

    Args:
        id_event (int): L'identifiant de l'événement.
        id_candidate (int): L'identifiant du candidat.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        # Si la connexion échoue, renvoie une erreur
        return "Erreur base de données"
    try:
        # Exécute la requête pour supprimer le candidat de l'événement
        conn.execute("DELETE FROM Participates WHERE id_event = ? AND id_candidate = ?", (id_event, id_candidate))
        # Sauvegarde les modifications
        conn.commit()
    except sqlite3.Error as e:
        # Gère les erreurs de requête SQL
        print(f"Erreur lors de la suppression du candidat: {e}")
        return "Erreur lors de la suppression du candidat"
    finally:
        # Ferme la connexion à la base de données
        conn.close()
    return None

# Participant functions

def create_participant(name, email):
    """
    Crée un nouveau participant dans la base de données.

    Args:
        name (str): Le nom du participant.
        email (str): L'adresse email du participant.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Participant (name_participant, email_participant) VALUES (?, ?)', (name, email))
        participant_id = cursor.lastrowid
        conn.commit()
        return participant_id, None
    except sqlite3.Error as e:
        print(f"Erreur lors de la création de l'intervenant: {e}")
        return None, "Erreur lors de la création de l'intervenant"
    finally:
        conn.close()

def get_all_participants():
    """
    Récupère tous les participants de la base de données.

    Returns:
        tuple: Un tuple contenant une liste de participants et un message d'erreur si une erreur est survenue.
    """
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
    """
    Récupère un participant de la base de données en utilisant son identifiant.

    Args:
        participant_id (int): L'identifiant du participant.

    Returns:
        tuple: Un tuple contenant le participant et un message d'erreur si une erreur est survenue.
    """
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

def get_participant_email(id_participant):
    """
    Récupère l'adresse email d'un candidat en utilisant son identifiant.

    Args:
        id_participant (int): L'identifiant du candidat.

    Returns:
        str: L'adresse email du candidat.
    """
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        participant = conn.execute('SELECT email_participant FROM Participant WHERE id_participant = ?', (id_participant,)).fetchone()
        return participant['email_participant']
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None
    finally:
        conn.close()

def edit_participant(name, email, id_participant):
    """
    Met à jour un participant dans la base de données.

    Args:
        name (str): Le nom du participant.
        email (str): L'adresse email du participant.
        id_participant (int): L'identifiant du participant.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
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
    """
    Supprime un participant de la base de données en utilisant son identifiant.

    Args:
        id_participant (int): L'identifiant du participant.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
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
    """
    Récupère les interviews associées à un participant.

    Args:
        id_participant (int): L'identifiant du participant.

    Returns:
        tuple: Un tuple contenant une liste d'interviews et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        interviews = conn.execute('''
        SELECT Interview.id_interview, Event.name_event, Event.date_event, Candidate.lastname_candidate, Candidate.name_candidate, Interview.feedback_participant, Interview.feedback_candidate, Interview.duration_interview
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

def get_last_added_participant():
    """
    Récupère le dernier participant ajouté à la base de données.

    Returns:
        tuple: Un tuple contenant le participant et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        participant = conn.execute('SELECT * FROM Participant ORDER BY id_participant DESC LIMIT 1').fetchone()
        return participant, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def delete_participant_from_event(id_event, id_participant):
    """
    Supprime un participant d'un événement.

    Args:
        id_event (int): L'identifiant de l'événement.
        id_participant (int): L'identifiant du participant.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute("DELETE FROM Attends WHERE id_event = ? AND id_participant = ?", (id_event, id_participant))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression de l'intervenant: {e}")
        return "Erreur lors de la suppression de l'intervenant"
    finally:
        conn.close()
    return None

def add_participant_to_event(id_event, id_participant):
    """
    Ajoute un participant à un événement.

    Args:
        id_event (int): L'identifiant de l'événement.
        id_participant (int): L'identifiant du participant.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute('INSERT INTO Attends (id_event, id_participant) VALUES (?, ?)', (id_event, id_participant))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout de l'intervenant à l'événement: {e}")
        return "Erreur lors de l'ajout de l'intervenant à l'événement"
    finally:
        conn.close()
    return None

# Interview functions

def create_interview(id_event, id_participant, id_candidate):
    """
    Crée un nouvel interview dans la base de données.

    Args:
        id_event (int): L'identifiant de l'événement.
        id_participant (int): L'identifiant du participant.
        id_candidate (int): L'identifiant du candidat.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
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
    """
    Récupère un interview de la base de données en utilisant son identifiant.

    Args:
        id_interview (int): L'identifiant de l'interview.

    Returns:
        tuple: Un tuple contenant l'interview et un message d'erreur si une erreur est survenue.
    """
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

def update_interview_status(interview_id, status):
    """
    Met à jour le statut d'un entretien.

    Args:
        interview_id (int): L'identifiant de l'entretien.
        status (int): Le nouveau statut de l'entretien.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    try:
        conn.execute('UPDATE Interview SET happened = ? WHERE id_interview = ?', (status, interview_id))
        conn.commit()
        return None
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour de l'entretien: {e}")
        return "Erreur lors de la mise à jour de l'entretien"
    finally:
        conn.close()

def get_candidate_from_event_participants_inverviews(id_event, id_participant):
    """
    Récupère les candidats associés aux interviews d'un participant pour un événement.

    Args:
        id_event (int): L'identifiant de l'événement.
        id_participant (int): L'identifiant du participant.

    Returns:
        tuple: Un tuple contenant une liste d'interviews et un message d'erreur si une erreur est survenue.
    """
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

def delete_interview(id_interview):
    """
    Supprime un interview de la base de données en utilisant son identifiant.

    Args:
        id_interview (int): L'identifiant de l'interview.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
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

def get_interview_by_candidate_event_participant(id_candidate, id_event, id_participant):
    """
    Récupère un entretien en utilisant l'identifiant du candidat, de l'événement et du participant.

    Args:
        id_candidate (int): L'identifiant du candidat.
        id_event (int): L'identifiant de l'événement.
        id_participant (int): L'identifiant du participant.

    Returns:
        tuple: Un tuple contenant l'entretien et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        interview = conn.execute('''
        SELECT * FROM Interview
        WHERE id_candidate = ? AND id_event = ? AND id_participant = ?
        ''', (id_candidate, id_event, id_participant)).fetchone()
        return interview, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

# Tag functions

def create_tag(name):
    """
    Crée un nouveau tag dans la base de données.

    Args:
        name (str): Le nom du tag.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
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
    """
    Récupère tous les tags de la base de données.

    Returns:
        tuple: Un tuple contenant une liste de tags et un message d'erreur si une erreur est survenue.
    """
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
    """
    Récupère un tag de la base de données en utilisant son identifiant.

    Args:
        tag_id (int): L'identifiant du tag.

    Returns:
        tuple: Un tuple contenant le tag et un message d'erreur si une erreur est survenue.
    """
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
    """
    Met à jour un tag dans la base de données.

    Args:
        name (str): Le nom du tag.
        id_tag (int): L'identifiant du tag.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
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
    """
    Supprime un tag de la base de données en utilisant son identifiant.

    Args:
        id_tag (int): L'identifiant du tag.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
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
    """
    Récupère les tags associés à un candidat.

    Args:
        id_candidate (int): L'identifiant du candidat.

    Returns:
        tuple: Un tuple contenant une liste de tags et un message d'erreur si une erreur est survenue.
    """
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
    """
    Ajoute un tag à un candidat.

    Args:
        id_candidate (int): L'identifiant du candidat.
        id_tag (int): L'identifiant du tag.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
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
    """
    Supprime un tag d'un candidat.

    Args:
        id_candidate (int): L'identifiant du candidat.
        id_tag (int): L'identifiant du tag.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
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
    """
    Récupère les tags associés à un participant.

    Args:
        id_participant (int): L'identifiant du participant.

    Returns:
        tuple: Un tuple contenant une liste de tags et un message d'erreur si une erreur est survenue.
    """
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
    """
    Ajoute un tag à un participant.

    Args:
        id_participant (int): L'identifiant du participant.
        id_tag (int): L'identifiant du tag.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
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
    """
    Supprime un tag d'un participant.

    Args:
        id_participant (int): L'identifiant du participant.
        id_tag (int): L'identifiant du tag.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
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
    """
    Récupère les tags associés à un événement.

    Args:
        id_event (int): L'identifiant de l'événement.

    Returns:
        tuple: Un tuple contenant une liste de tags et un message d'erreur si une erreur est survenue.
    """
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
    """
    Ajoute un tag à un événement.

    Args:
        id_event (int): L'identifiant de l'événement.
        id_tag (int): L'identifiant du tag.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
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
    """
    Supprime un tag d'un événement.

    Args:
        id_event (int): L'identifiant de l'événement.
        id_tag (int): L'identifiant du tag.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
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

def get_last_added_event():
    """
    Récupère le dernier événement ajouté à la base de données.

    Returns:
        tuple: Un tuple contenant l'événement et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        event = conn.execute('SELECT * FROM Event ORDER BY id_event DESC LIMIT 1').fetchone()
        return event, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

# Attends and Participates functions

def edit_participates(id_candidat, id_event, priority):
    """
    Met à jour la priorité d'un candidat pour un événement.

    Args:
        id_candidat (int): L'identifiant du candidat.
        id_event (int): L'identifiant de l'événement.
        priority (int): La priorité du candidat pour l'événement.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute('UPDATE Participates SET priority = ? WHERE id_candidate = ? AND id_event = ?', (priority, id_candidat, id_event))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour de la priorité du candidat: {e}")
        return "Erreur lors de la mise à jour de la priorité du candidat"
    finally:
        conn.close()
    return None

def create_participates(id_candidate, id_event, priority):
    """
    Crée une nouvelle participation dans la base de données.

    Args:
        id_candidate (int): L'identifiant du candidat.
        id_event (int): L'identifiant de l'événement.
        priority (int): La priorité du candidat pour l'événement.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute('INSERT INTO Participates (id_candidate, id_event, priority) VALUES (?, ?, ?)', (id_candidate, id_event, priority))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la création de la participation: {e}")
        return "Erreur lors de la création de la participation"
    finally:
        conn.close()
    return None

def delete_participates(id_candidate, id_event):
    """
    Supprime une participation de la base de données en utilisant l'identifiant du candidat et de l'événement.

    Args:
        id_candidate (int): L'identifiant du candidat.
        id_event (int): L'identifiant de l'événement.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute("DELETE FROM Participates WHERE id_candidate = ? AND id_event = ?", (id_candidate, id_event))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression de la participation: {e}")
        return "Erreur lors de la suppression de la participation"
    finally:
        conn.close()
    return None

def create_attends(id_participant, id_event):
    """
    Crée une nouvelle participation dans la base de données.

    Args:
        id_participant (int): L'identifiant du participant.
        id_event (int): L'identifiant de l'événement.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute('INSERT INTO Attends (id_participant, id_event) VALUES (?, ?)', (id_participant, id_event))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la création de la participation: {e}")
        return "Erreur lors de la création de la participation"
    finally:
        conn.close()
    return None

def delete_attends(id_participant, id_event):
    """
    Supprime une participation de la base de données en utilisant l'identifiant du participant et de l'événement.

    Args:
        id_participant (int): L'identifiant du participant.
        id_event (int): L'identifiant de l'événement.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute("DELETE FROM Attends WHERE id_participant = ? AND id_event = ?", (id_participant, id_event))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression de la participation: {e}")
        return "Erreur lors de la suppression de la participation"
    finally:
        conn.close()
    return None

# Authentication functions

def auth_get_session(username):
    """
    Récupère la session d'un utilisateur en utilisant son nom d'utilisateur.

    Args:
        username (str): Le nom d'utilisateur de l'utilisateur.

    Returns:
        tuple: Un tuple contenant la session et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        session = conn.execute('SELECT session_token FROM User WHERE username = ?', (username,)).fetchone()
        return session, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def auth_get_hashedpassword(username):
    """
    Récupère le mot de passe hashé d'un utilisateur en utilisant son nom d'utilisateur.

    Args:
        username (str): Le nom d'utilisateur de l'utilisateur.

    Returns:
        tuple: Un tuple contenant le mot de passe hashé et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        password_user = conn.execute('SELECT password_user FROM User WHERE username = ?', (username,)).fetchone()
        return password_user, None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def update_user_password(username, password, session_token):
    """
    Met à jour le mot de passe et le sel d'un utilisateur dans la base de données.

    Args:
        id_user (int): L'identifiant de l'utilisateur.
        password (str): Le nouveau mot de passe haché de l'utilisateur.
        salt (str): Le nouveau sel de l'utilisateur.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE User SET password_user = ?, session_token = ? WHERE username = ?', (password, session_token, username))
        conn.commit()
        return None
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour du mot de passe de l'utilisateur: {e}")
        return "Erreur lors de la mise à jour du mot de passe de l'utilisateur"
    finally:
        conn.close()

def auth_register_candidate(id_candidate, username, password_user, session_token):
    """
    Enregistre un candidat dans la base de données.

    Args:
        id_candidate (int): L'identifiant du candidat.
        username (str): Le nom d'utilisateur du candidat.
        password_user (str): Le mot de passe hashé du candidat.
        session_token (str): Le jeton de session du candidat.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute('INSERT INTO User (username, password_user, session_token) VALUES (?, ?, ?)', (username, password_user, session_token))
        conn.commit()
        # get latest user id
        user_id = conn.execute('SELECT id_user FROM User WHERE username = ?', (username,)).fetchone()
        # add user to candidate table
        conn.execute('UPDATE Candidate SET id_user = ? WHERE id_candidate = ?', (user_id[0], id_candidate))
        return None
    except sqlite3.Error as e:
        print(f"Erreur lors de l'enregistrement du candidat: {e}")
        return "Erreur lors de l'enregistrement du candidat"
    finally:
        conn.close()

def auth_register_employee(id_employee, username, password_user, session_token):
    """
    Enregistre un employé dans la base de données.

    Args:
        id_employee (int): L'identifiant de l'employé.
        username (str): Le nom d'utilisateur de l'employé.
        password_user (str): Le mot de passe hashé de l'employé.
        session_token (str): Le jeton de session de l'employé.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        conn.execute('INSERT INTO User (username, password_user, session_token) VALUES (?, ?, ?)', (username, password_user, session_token))
        conn.commit()
        # get latest user id
        user_id = conn.execute('SELECT id_user FROM User WHERE username = ?', (username,)).fetchone()
        # add user to employee table
        conn.execute('UPDATE Office SET id_user = ? WHERE id_employee = ?', (user_id[0], id_employee))
        return None
    except sqlite3.Error as e:
        print(f"Erreur lors de l'enregistrement de l'employé: {e}")
        return "Erreur lors de l'enregistrement de l'employé"
    finally:
        conn.close()

def get_user_permissions(user_id):
    """
    Récupère les permissions associées à un identifiant utilisateur donné depuis la base de données.

    Args:
        user_id (int): L'identifiant de l'utilisateur dont les permissions doivent être récupérées.

    Returns:
        tuple: Un tuple contenant :
            - list: Une liste de noms de permissions associées à l'utilisateur.
            - str: Un message d'erreur si une erreur est survenue, sinon None.

    Raises:
        sqlite3.Error: Si une erreur de base de données survient lors de l'exécution de la requête.
    """
    conn = get_db_connection()
    try:
        permissions = conn.execute('''
        SELECT Permission.name_permission
        FROM Permission
        JOIN Role_permission ON Permission.id_permission = Role_permission.id_permission
        JOIN User_role ON Role_permission.id_role = User_role.id_role
        WHERE User_role.id_user = ?
        ''', (user_id,)).fetchall()
        return [permission['name_permission'] for permission in permissions], None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def auth_get_perms_from_session(session_token):
    """
    Récupère les permissions associées à une session donnée depuis la base de données.

    Args:
        session_token (str): Le jeton de session dont les permissions doivent être récupérées.

    Returns:
        tuple: Un tuple contenant :
            - list: Une liste de noms de permissions associées à la session.
            - str: Un message d'erreur si une erreur est survenue, sinon None.

    Raises:
        sqlite3.Error: Si une erreur de base de données survient lors de l'exécution de la requête.
    """
    conn = get_db_connection()
    try:
        permissions = conn.execute('''
        SELECT Permission.name_permission
        FROM Permission
        JOIN Role_permission ON Permission.id_permission = Role_permission.id_permission
        JOIN User_role ON Role_permission.id_role = User_role.id_role
        JOIN User ON User_role.id_user = User.id_user
        WHERE User.session_token = ?
        ''', (str(session_token),)).fetchall()
        return [permission['name_permission'] for permission in permissions], None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def auth_is_superuser(session_token):
    """
    Vérifie si un utilisateur est un super-utilisateur.

    Args:
        session_token (str): Le jeton de session de l'utilisateur.

    Returns:
        bool: True si l'utilisateur est un super-utilisateur, False sinon.
    """
    conn = get_db_connection()
    try:
        is_superuser = conn.execute('''
        SELECT Role.name_role
        FROM Role
        JOIN User_role ON Role.id_role = User_role.id_role
        JOIN User ON User_role.id_user = User.id_user
        WHERE User.session_token = ? AND Role.name_role = 'superadmin'
        ''', (str(session_token),)).fetchone()
        return is_superuser is not None
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return False
    finally:
        conn.close()

# Employee functions

def create_employee(lastname, name, email, role):
    """
    Crée un nouvel employé dans la base de données.

    Args:
        lastname (str): Le nom de famille de l'employé.
        name (str): Le prénom de l'employé.
        email (str): L'adresse email de l'employé.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        # Insere l'employé dans la base de données
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Office (lastname_employee, name_employee, email_employee) VALUES (?, ?, ?)', (lastname, name, email))
        employee_id = cursor.lastrowid

       # Récupère l'id_role correspondant au nom du rôle
        role_id = cursor.execute('SELECT id_role FROM Role WHERE name_role = ?', (role,)).fetchone()
        if role_id is None:
            return None, "Rôle non trouvé"

        # Insere l'association de l'employé avec le rôle dans la table User_role
        cursor.execute('INSERT INTO User_role (id_user, id_role) VALUES (?, ?)', (employee_id, role_id[0]))

        # Sauvegarde les modifications
        conn.commit()
        return employee_id, None
    except sqlite3.Error as e:
        print(f"Erreur lors de la création de l'employé: {e}")
        return None, "Erreur lors de la création de l'employé"
    finally:
        # Ferme la connexion à la base de données
        conn.close()

def get_employee_email(id_employee):
    """
    Récupère l'adresse email d'un employé en utilisant son identifiant.

    Args:
        id_employee (int): L'identifiant de l'employé.

    Returns:
        str: L'adresse email de l'employé.
    """
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        employee = conn.execute('SELECT email_employee FROM Office WHERE id_employee = ?', (id_employee,)).fetchone()
        return employee['email_employee']
    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None
    finally:
        conn.close()

def get_all_employees():
    """
    Récupère tous les employés de la base de données.

    Returns:
        tuple: Un tuple contenant une liste d'employés et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"

    try:
        # Renvoie tous les employés de la base de données
        employees = conn.execute('SELECT * FROM Office').fetchall()

        if employees:
            return employees, None
        else:
            return None, "Pas d'employé"

    except sqlite3.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"

    finally:
        # Fermes la connexion à la base de données
        conn.close()

def get_employee(employee_id):
    """
    Récupère un employé de la base de données en utilisant son identifiant.

    Args:
        employee_id (int): L'identifiant de l'employé.

    Returns:
        tuple: Un tuple contenant l'employé et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        # Si la connexion échoue, renvoie une erreur
        return None, "Erreur base de données"
    try:
        # Exécute la requête pour récupérer l'employé
        employee = conn.execute('SELECT * FROM Office WHERE id_employee = ?', (employee_id,)).fetchone()
        return employee, None
    except sqlite3.Error as e:
        # Gère les erreurs de requête SQL
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        # Ferme la connexion à la base de données
        conn.close()

def edit_employee(lastname, name, email, id_employee):
    """
    Met à jour un employé dans la base de données.

    Args:
        lastname (str): Le nom de famille de l'employé.
        name (str): Le prénom de l'employé.
        email (str): L'adresse email de l'employé.
        id_employee (int): L'identifiant de l'employé.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"

    try:
        # Met à jour l'employé dans la base de données
        conn.execute('UPDATE Office SET lastname_employee = ?, name_employee = ?, email_employee = ? WHERE id_employee = ?', (lastname, name, email, id_employee))
        # Sauvegarde les modifications
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour de l'employé: {e}")
        return "Erreur lors de la mise à jour de l'employé"
    finally:
        # Fermes la connexion à la base de données
        conn.close()
    return None

def delete_employee(id_employee):
    """
    Supprime un employé de la base de données en utilisant son identifiant.

    Args:
        id_employee (int): L'identifiant de l'employé.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        # Si la connexion échoue, renvoie une erreur
        return "Erreur base de données"
    try:
        # Exécute la requête pour supprimer l'employé
        conn.execute("DELETE FROM Office WHERE id_employee = ?", (id_employee,))
        # Sauvegarde les modifications
        conn.commit()
    except sqlite3.Error as e:
        # Gère les erreurs de requête SQL
        print(f"Erreur lors de la suppression de l'employé: {e}")
        return "Erreur lors de la suppression de l'employé"
    finally:
        # Ferme la connexion à la base de données
        conn.close()
    return None