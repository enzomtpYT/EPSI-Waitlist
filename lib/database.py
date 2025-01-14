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

def get_event_candidates(todayevent):
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
        # Insere le candidat dans la base de données
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Candidate (lastname_candidate, name_candidate, email_candidate) VALUES (?, ?, ?)', (lastname, name, email))
        candidate_id = cursor.lastrowid
        # Sauvegarde les modifications
        conn.commit()
        return candidate_id, None
    except sqlite3.Error as e:
        print(f"Erreur lors de la création du candidat: {e}")
        return None, "Erreur lors de la création du candidat"
    finally:
        # Fermes la connexion à la base de données
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