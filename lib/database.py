import psycopg2, datetime
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

def get_db_connection():
    # Load environment variables from .env file
    load_dotenv()
    """
    Établit une connexion à la base de données PostgreSQL.

    Returns:
        psycopg2.extensions.connection: L'objet de connexion à la base de données.
        None: Si une erreur survient lors de la connexion.
    """
    try:
        conn = psycopg2.connect(os.getenv('db_url'))
        conn.autocommit = True
        return conn
    except psycopg2.Error as e:
        print(f"Erreur base de données: {e}")
        return None

today = datetime.date.today()

# Event functions

def create_event(name, date, has_timeslots, start_time_event=None, end_time_event=None):
    """
    Crée un nouvel événement dans la base de données.

    Args:
        name (str): Le nom de l'événement.
        date (str): La date de l'événement.
        has_timeslots (bool): Si l'événement a des créneaux horaires.
        start_time_event=None (str): L'heure de début de l'événement.
        end_time_event=None (str): L'heure de fin de l'événement.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Event (name_event, date_event, has_timeslots, start_time_event, end_time_event) VALUES (%s, %s, %s, %s, %s) RETURNING id_event', (name, date, has_timeslots, start_time_event, end_time_event))
        event_id = cursor.fetchone()[0]
        return event_id, None
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM Event')
        events = cursor.fetchall()
        if events:
            return events, None
        else:
            return None, "Pas d'événement aujourd'hui"
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM Event WHERE id_event = %s', (event_id,))
        event = cursor.fetchone()
        return event, None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def edit_event(name, date, id_event, has_timeslots, start_time_event=None, end_time_event=None):
    """
    Met à jour un événement dans la base de données.

    Args:
        name (str): Le nom de l'événement.
        date (str): La date de l'événement.
        id_event (int): L'identifiant de l'événement.
        has_timeslots (bool): Si l'événement a des créneaux horaires.
        start_time_event=None (str): L'heure de début de l'événement.
        end_time_event=None (str): L'heure de fin de l'événement.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE Event SET name_event = %s, date_event = %s, has_timeslots = %s, start_time_event = %s, end_time_event = %s WHERE id_event = %s', (name, date, has_timeslots, start_time_event, end_time_event, id_event))
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Event WHERE id_event = %s", (id_event,))
    except psycopg2.Error as e:
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
        return None, None, "Erreur base de données"
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM Event WHERE id_event = %s', (id_event,))
        event = cursor.fetchone()
        cursor.execute('''
        SELECT Interview.id_interview, Participant.name_participant, Candidate.lastname_candidate, Candidate.name_candidate, Interview.feedback_participant, Interview.feedback_candidate, Interview.duration_interview
        FROM Interview
        JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate
        JOIN Participant ON Interview.id_participant = Participant.id_participant
        JOIN Event ON Interview.id_event = Event.id_event
        WHERE Interview.id_event = %s AND Interview.happened = TRUE
        ''', (id_event,))
        interviews = cursor.fetchall()
        return event, interviews, None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, None, "Erreur requête base de données"
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id_event FROM Event WHERE date_event = %s', (today,))
        events = cursor.fetchall()
        if events:
            return events[0]['id_event'], None
        else:
            return None, "Pas d'événement aujourd'hui"
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
        SELECT Candidate.*, Attends.priority
        FROM Candidate
        JOIN Attends ON Candidate.id_candidate = Attends.id_candidate
        WHERE Attends.id_event = %s
        ''', (id,))
        candidates = cursor.fetchall()
        return candidates, None
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
        SELECT Participant.*
        FROM Participant
        JOIN Participates ON Participant.id_participant = Participates.id_participant
        WHERE Participates.id_event = %s
        ''', (id,))
        inter = cursor.fetchall()
        return inter, None
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
        SELECT Interview.id_candidate, Candidate.lastname_candidate, Candidate.name_candidate, Candidate.email_candidate, Interview.id_interview 
        FROM Interview 
        JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate 
        WHERE id_event = %s AND id_participant = %s AND happened = %s
        ''', (todayevent, id_participant, False))
        candid = cursor.fetchall()
        return candid, None
    except psycopg2.Error as e:
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
        cursor.execute('INSERT INTO "User" (username) VALUES (%s) RETURNING id_user', (email,))
        user_id = cursor.fetchone()[0]

        # Insere le candidat dans la base de données
        cursor.execute('INSERT INTO Candidate (lastname_candidate, name_candidate, email_candidate, id_user) VALUES (%s, %s, %s, %s) RETURNING id_candidate', (lastname, name, email, user_id))
        candidate_id = cursor.fetchone()[0]

        # Assigne le rôle "candidate" à l'utilisateur
        cursor.execute('INSERT INTO User_role (id_user, id_role) VALUES (%s, (SELECT id_role FROM Role WHERE name_role = %s))', (user_id, 'candidate'))

        # Sauvegarde les modifications
        conn.commit()
        return candidate_id, None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute('SELECT email_candidate FROM Candidate WHERE id_candidate = %s', (id_candidate,))
        candidate = cursor.fetchone()
        return candidate[0] if candidate else None
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM Candidate')
        candidates = cursor.fetchall()

        if candidates:
            return candidates, None
        else:
            return None, "Pas de candidat"

    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM Candidate WHERE id_candidate = %s', (candidate_id,))
        candidate = cursor.fetchone()
        return candidate, None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        # Met à jour le candidat dans la base de données
        cursor.execute('UPDATE Candidate SET lastname_candidate = %s, name_candidate = %s, email_candidate = %s WHERE id_candidate = %s', (lastname, name, email, id_candidate))
        # Sauvegarde les modifications
        conn.commit()
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        # Supprime l'utilisateur associé au candidat (candidat supprimé en cascade)
        cursor.execute('DELETE FROM "User" WHERE id_user = (SELECT id_user FROM Candidate WHERE id_candidate = %s)', (id_candidate,))
        # Sauvegarde les modifications
        conn.commit()
    except psycopg2.Error as e:
        # Gère les erreurs de requête SQL
        print(f"Erreur lors de la suppression du candidat: {e}")
        return "Erreur lors de la suppression du candidat"
    finally:
        # Ferme la connexion à la base de données
        conn.close()
    return None

def get_candidate_events(id_candidate):
    """
    Récupère les événements associés à un candidat.

    Args:
        id_candidate (int): L'identifiant du candidat.

    Returns:
        tuple: Un tuple contenant une liste d'événements et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Renvoie les événements du candidat
        cursor.execute('''
        SELECT Event.id_event, Event.name_event, Event.date_event
        FROM Event
        JOIN Attends ON Event.id_event = Attends.id_event
        WHERE Attends.id_candidate = %s
        ''', (id_candidate,))
        events = cursor.fetchall()

        return events, None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        # Ferme la connexion à la base de données
        conn.close()

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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Renvoie les entretiens du candidat
        cursor.execute('''
        SELECT Interview.id_interview, Event.name_event, Event.date_event, Participant.name_participant, Interview.feedback_candidate, Interview.feedback_participant, Interview.duration_interview
        FROM Interview
        JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate
        JOIN Participant ON Interview.id_participant = Participant.id_participant
        JOIN Event ON Interview.id_event = Event.id_event
        WHERE Interview.id_candidate = %s AND Interview.happened = TRUE
        ''', (id_candidate,))
        interviews = cursor.fetchall()

        return interviews, None
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Renvoie le dernier candidat ajouté
        cursor.execute('SELECT * FROM Candidate ORDER BY id_candidate DESC LIMIT 1')
        candidate = cursor.fetchone()
        return candidate, None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        # Exécute la requête pour supprimer le candidat de tous les entretiens associés à l'événement
        cursor.execute("DELETE FROM Interview WHERE id_event = %s AND id_candidate = %s", (id_event, id_candidate))
        # Sauvegarde les modifications
        conn.commit()
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        # Exécute la requête pour ajouter le candidat à l'événement
        cursor.execute('INSERT INTO Attends (id_event, id_candidate) VALUES (%s, %s)', (id_event, id_candidate))
        # Sauvegarde les modifications
        conn.commit()
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        # Exécute la requête pour supprimer le candidat de l'événement
        cursor.execute("DELETE FROM Attends WHERE id_event = %s AND id_candidate = %s", (id_event, id_candidate))
        # Sauvegarde les modifications
        conn.commit()
    except psycopg2.Error as e:
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

        # Insère l'utilisateur dans la table User
        cursor.execute('INSERT INTO "User" (username) VALUES (%s) RETURNING id_user', (email,))
        user_id = cursor.fetchone()[0]

        # Insere l'intervenant dans la base de données
        cursor.execute('INSERT INTO Participant (name_participant, email_participant, id_user) VALUES (%s, %s, %s) RETURNING id_participant', (name, email, user_id))
        participant_id = cursor.fetchone()[0]

        # Assigne le rôle "participant" à l'utilisateur
        cursor.execute('INSERT INTO User_role (id_user, id_role) VALUES (%s, (SELECT id_role FROM Role WHERE name_role = %s))', (user_id, 'participant'))

        # Sauvegarde les modifications
        conn.commit()
        return participant_id, None
    except psycopg2.Error as e:
        print(f"Erreur lors de la création de l'intervenant: {e}")
        return None, "Erreur lors de la création de l'intervenant"
    finally:
        # Fermes la connexion à la base de données
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM Participant')
        participants = cursor.fetchall()
        if participants:
            return participants, None
        else:
            return None, "Pas d'intervenant"
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM Participant WHERE id_participant = %s', (participant_id,))
        participant = cursor.fetchone()
        return participant, None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_participant_email(id_participant):
    """
    Récupère l'adresse email d'un intervenant en utilisant son identifiant.

    Args:
        id_participant (int): L'identifiant de l'intervenant.

    Returns:
        str: L'adresse email de l'intervenant.
    """
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT email_participant FROM Participant WHERE id_participant = %s', (id_participant,))
        participant = cursor.fetchone()
        return participant['email_participant']
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute('UPDATE Participant SET name_participant = %s, email_participant = %s WHERE id_participant = %s', (name, email, id_participant))
        conn.commit()
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        # Supprime l'utilisateur associé au participant (participant supprimé en cascade)
        cursor.execute('DELETE FROM "User" WHERE id_user = (SELECT id_user FROM Participant WHERE id_participant = %s)', (id_participant,)) 
        conn.commit()
    except psycopg2.Error as e:
        print(f"Erreur lors de la suppression de l'intervenant: {e}")
        return "Erreur lors de la suppression de l'intervenant"
    finally:
        conn.close()
    return None

def get_participant_events(id_participant):
    """
    Récupère les événements associés à un participant.

    Args:
        id_participant (int): L'identifiant du participant.

    Returns:
        tuple: Un tuple contenant une liste d'événements et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
        SELECT Event.id_event, Event.name_event, Event.date_event
        FROM Event
        JOIN Participates ON Event.id_event = Participates.id_event
        WHERE Participates.id_participant = %s
        ''', (id_participant,))
        events = cursor.fetchall()
        return events, None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
        SELECT Interview.id_interview, Event.name_event, Event.date_event, Candidate.lastname_candidate, Candidate.name_candidate, Interview.feedback_participant, Interview.feedback_candidate, Interview.duration_interview
        FROM Interview
        JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate
        JOIN Participant ON Interview.id_participant = Participant.id_participant
        JOIN Event ON Interview.id_event = Event.id_event
        WHERE Interview.id_participant = %s AND Interview.happened = TRUE
        ''', (id_participant,))
        interviews = cursor.fetchall()
        return interviews, None
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM Participant ORDER BY id_participant DESC LIMIT 1')
        participant = cursor.fetchone()
        return participant, None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Participates WHERE id_event = %s AND id_participant = %s", (id_event, id_participant))
        conn.commit()
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Participates (id_event, id_participant) VALUES (%s, %s)', (id_event, id_participant))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Erreur lors de l'ajout de l'intervenant à l'événement: {e}")
        return "Erreur lors de l'ajout de l'intervenant à l'événement"
    finally:
        conn.close()
    return None

# Interview functions

def get_user_past_interviews(session_token):
    """
    Récupère les entretiens passés d'un utilisateur.

    Args:
        session_token (str): Le token de session de l'utilisateur.

    Returns:
        tuple: Un tuple contenant une liste d'entretiens et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "User" WHERE session_token = %s', (session_token,))
        user = cursor.fetchone()
        if user:
            # Check if user is a candidate
            cursor.execute('SELECT * FROM Candidate WHERE id_user = %s', (user['id_user'],))
            candidate = cursor.fetchone()
            if candidate:
                cursor.execute('''
                SELECT Interview.id_interview, Participant.name_participant, Event.name_event, Event.date_event, Interview.feedback_participant, Interview.feedback_candidate, Interview.duration_interview
                FROM Interview
                JOIN Participant ON Interview.id_participant = Participant.id_participant
                JOIN Event ON Interview.id_event = Event.id_event
                WHERE Interview.id_candidate = %s AND Interview.happened = TRUE
                ''', (candidate['id_candidate'],))
                interviews = cursor.fetchall()
                return interviews, None

            # Check if user is a participant
            cursor.execute('SELECT * FROM Participant WHERE id_user = %s', (user['id_user'],))
            participant = cursor.fetchone()
            if participant:
                cursor.execute('''
                SELECT Interview.id_interview, Candidate.lastname_candidate, Candidate.name_candidate, Event.name_event, Event.date_event, Interview.feedback_participant, Interview.feedback_candidate, Interview.duration_interview
                FROM Interview
                JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate
                JOIN Event ON Interview.id_event = Event.id_event
                WHERE Interview.id_participant = %s AND Interview.happened = TRUE
                ''', (participant['id_participant'],))
                interviews = cursor.fetchall()
                return interviews, None

            return None, "Utilisateur non trouvé"
        else:
            return None, "Utilisateur non trouvé"
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

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
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Interview (id_event, id_participant, id_candidate, happened) VALUES (%s, %s, %s, 0)', (id_event, id_participant, id_candidate))
        conn.commit()
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM Interview WHERE id_interview = %s', (id_interview,))
        interview = cursor.fetchone()
        return interview, None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute('UPDATE Interview SET happened = %s WHERE id_interview = %s', (status, interview_id))
        conn.commit()
        return None
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
        SELECT Interview.id_interview, Candidate.lastname_candidate, Candidate.name_candidate, Candidate.id_candidate
        FROM Interview
        JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate
        WHERE Interview.id_event = %s AND Interview.id_participant = %s
        ''', (id_event, id_participant))
        interviews = cursor.fetchall()
        return interviews, None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Interview WHERE id_interview = %s", (id_interview,))
        conn.commit()
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
        SELECT * FROM Interview
        WHERE id_candidate = %s AND id_event = %s AND id_participant = %s
        ''', (id_candidate, id_event, id_participant))
        interview = cursor.fetchone()
        return interview, None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Tag (name_tag) VALUES (%s)', (name,))
        conn.commit()
        return None
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM Tag')
        tags = cursor.fetchall()
        if tags:
            return tags, None
        else:
            return [], "Pas de tag"
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM Tag WHERE id_tag = %s', (tag_id,))
        tag = cursor.fetchone()
        return tag, None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute('UPDATE Tag SET name_tag = %s WHERE id_tag = %s', (name, id_tag))
        conn.commit()
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Tag WHERE id_tag = %s", (id_tag,))
        conn.commit()
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
        SELECT Tag.id_tag, Tag.name_tag
        FROM Tag
        JOIN Candidate_tag ON Tag.id_tag = Candidate_tag.id_tag
        WHERE Candidate_tag.id_candidate = %s
        ''', (id_candidate,))
        tags = cursor.fetchall()
        return tags, None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Candidate_tag (id_candidate, id_tag) VALUES (%s, %s)', (id_candidate, id_tag))
        conn.commit()
        return None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Candidate_tag WHERE id_candidate = %s AND id_tag = %s', (id_candidate, id_tag))
        conn.commit()
        return None
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
        SELECT Tag.id_tag, Tag.name_tag
        FROM Tag
        JOIN Participant_tag ON Tag.id_tag = Participant_tag.id_tag
        WHERE Participant_tag.id_participant = %s
        ''', (id_participant,))
        tags = cursor.fetchall()
        return tags, None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Participant_tag (id_participant, id_tag) VALUES (%s, %s)', (id_participant, id_tag))
        conn.commit()
        return None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Participant_tag WHERE id_participant = %s AND id_tag = %s', (id_participant, id_tag))
        conn.commit()
        return None
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
        SELECT Tag.*
        FROM Tag
        JOIN Event_tag ON Tag.id_tag = Event_tag.id_tag
        WHERE Event_tag.id_event = %s
        ''', (id_event,))
        tags = cursor.fetchall()
        return tags, None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Event_tag (id_event, id_tag) VALUES (%s, %s)', (id_event, id_tag))
        conn.commit()
        return None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Event_tag WHERE id_event = %s AND id_tag = %s', (id_event, id_tag))
        conn.commit()
        return None
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM Event ORDER BY id_event DESC LIMIT 1')
        event = cursor.fetchone()
        return event, None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

# Attends and Participates functions

def edit_attends(id_candidat, id_event, priority):
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
        cursor = conn.cursor()
        cursor.execute('UPDATE Attends SET priority = %s WHERE id_candidate = %s AND id_event = %s', (priority, id_candidat, id_event))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Erreur lors de la mise à jour de la priorité du candidat: {e}")
        return "Erreur lors de la mise à jour de la priorité du candidat"
    finally:
        conn.close()
    return None

def create_attends(id_candidate, id_event, priority):
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
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Attends (id_candidate, id_event, priority) VALUES (%s, %s, %s)', (id_candidate, id_event, priority))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Erreur lors de la création de la participation (Candidat): {e}")
        return "Erreur lors de la création de la participation (Candidat)"
    finally:
        conn.close()
    return None

def delete_attends(id_candidate, id_event):
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
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Attends WHERE id_candidate = %s AND id_event = %s", (id_candidate, id_event))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Erreur lors de la suppression de la participation: {e}")
        return "Erreur lors de la suppression de la participation"
    finally:
        conn.close()
    return None

def create_participates(id_participant, id_event):
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
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Participates (id_participant, id_event) VALUES (%s, %s)', (id_participant, id_event))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Erreur lors de la création de la participation (Intervenant): {e}")
        return "Erreur lors de la création de la participation (Intervenant)"
    finally:
        conn.close()
    return None

def delete_participates(id_participant, id_event):
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
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Participates WHERE id_participant = %s AND id_event = %s", (id_participant, id_event))
        conn.commit()
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute('SELECT session_token FROM "User" WHERE username = %s', (username,))
        session = cursor.fetchone()
        return session[0], None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute('SELECT password_user FROM "User" WHERE username = %s', (username,))
        password_user = cursor.fetchone()
        return password_user, None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def update_user_password(username, password, session_token):
    """
    Met à jour le mot de passe et le sel d'un utilisateur dans la base de données.

    Args:
        username (str): L'username de l'utilisateur.
        password (str): Le nouveau mot de passe haché de l'utilisateur.
        session_token (str): Le token de session de l'utilisateur.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE "User" SET password_user = %s, session_token = %s WHERE username = %s', (password, session_token, username))
        conn.commit()
        return None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute('INSERT INTO "User" (username, password_user, session_token) VALUES (%s, %s, %s)', (username, password_user, session_token))
        conn.commit()
        # get latest user id
        cursor.execute('SELECT id_user FROM "User" WHERE username = %s', (username,))
        user_id = cursor.fetchone()
        # add user to candidate table
        cursor.execute('UPDATE Candidate SET id_user = %s WHERE id_candidate = %s', (user_id[0], id_candidate))
        conn.commit()
        return None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute('INSERT INTO "User" (username, password_user, session_token) VALUES (%s, %s, %s)', (username, password_user, session_token))
        conn.commit()
        # get latest user id
        cursor.execute('SELECT id_user FROM "User" WHERE username = %s', (username,))
        user_id = cursor.fetchone()
        # add user to employee table
        cursor.execute('UPDATE Employee SET id_user = %s WHERE id_employee = %s', (user_id[0], id_employee))
        conn.commit()
        return None
    except psycopg2.Error as e:
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
        psycopg2.Error: Si une erreur de base de données survient lors de l'exécution de la requête.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
        SELECT Permission.name_permission
        FROM Permission
        JOIN Role_permission ON Permission.id_permission = Role_permission.id_permission
        JOIN User_role ON Role_permission.id_role = User_role.id_role
        WHERE User_role.id_user = %s
        ''', (user_id,))
        permissions = cursor.fetchall()
        return [permission['name_permission'] for permission in permissions], None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_user_role_with_token(session_token):
    """
    Récupère le rôle d'un utilisateur en utilisant son jeton de session.

    Args:
        session_token (str): Le jeton de session de l'utilisateur.

    Returns:
        tuple: Un tuple contenant le rôle et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
        SELECT Role.name_role
        FROM Role
        JOIN User_role ON Role.id_role = User_role.id_role
        JOIN "User" ON User_role.id_user = "User".id_user
        WHERE "User".session_token = %s
        ''', (session_token,))
        role = cursor.fetchone()
        if role:
            return role['name_role']
        else:
            print("Rôle non trouvé")
            return None
    except psycopg2.Error as e:
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
        psycopg2.Error: Si une erreur de base de données survient lors de l'exécution de la requête.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
        SELECT Permission.name_permission
        FROM Permission
        JOIN Role_permission ON Permission.id_permission = Role_permission.id_permission
        JOIN User_role ON Role_permission.id_role = User_role.id_role
        JOIN "User" ON User_role.id_user = "User".id_user
        WHERE "User".session_token = %s
        ''', (str(session_token),))
        permissions = cursor.fetchall()
        return [permission['name_permission'] for permission in permissions], None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute('''
        SELECT Role.name_role
        FROM Role
        JOIN User_role ON Role.id_role = User_role.id_role
        JOIN "User" ON User_role.id_user = "User".id_user
        WHERE "User".session_token = %s AND Role.name_role = 'superadmin'
        ''', (str(session_token),))
        is_superuser = cursor.fetchone()
        return is_superuser is not None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return False
    finally:
        conn.close()

def auth_get_user_type(session_token):
    """
    Retourne le type d'utilisateur en fonction de son jeton de session.

    Args:
        session_token (str): Le jeton de session de l'utilisateur.

    Returns:
        str: Le type d'utilisateur ("candidat", "participant" ou "employee"), ou None si non trouvé.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
        SELECT Candidate.id_candidate
        FROM Candidate
        JOIN "User" ON Candidate.id_user = "User".id_user
        WHERE "User".session_token = %s
        ''', (str(session_token),))
        user_type = cursor.fetchone()
        if user_type:
            return "candidate"
        cursor.execute('''
        SELECT Participant.id_participant
        FROM Participant
        JOIN "User" ON Participant.id_user = "User".id_user
        WHERE "User".session_token = %s
        ''', (str(session_token),))
        user_type = cursor.fetchone()
        if user_type:
            return "participant"
        cursor.execute('''
        SELECT Employee.id_employee
        FROM Employee
        JOIN "User" ON Employee.id_user = "User".id_user
        WHERE "User".session_token = %s
        ''', (str(session_token),))
        user_type = cursor.fetchone()
        if user_type:
            return "employee"
        return None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None
    finally:
        conn.close()

def auth_get_type_id(session_token):
    """
    Retourne l'id du type utilisateur (employee, candidate, participant) en fonction de son jeton de session.

    Args:
        session_token (str): Le jeton de session de l'utilisateur.

    Returns:
        tuple: Un tuple contenant l'id du type utilisateur et un message d'erreur si une erreur est survenue.
    """
    conn = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
        SELECT Candidate.id_candidate
        FROM Candidate
        JOIN "User" ON Candidate.id_user = "User".id_user
        WHERE "User".session_token = %s
        ''', (str(session_token),))
        user_type = cursor.fetchone()
        if user_type:
            return user_type['id_candidate'], None
        cursor.execute('''
        SELECT Participant.id_participant
        FROM Participant
        JOIN "User" ON Participant.id_user = "User".id_user
        WHERE "User".session_token = %s
        ''', (str(session_token),))
        user_type = cursor.fetchone()
        if user_type:
            return user_type['id_participant'], None
        cursor.execute('''
        SELECT Employee.id_employee
        FROM Employee
        JOIN "User" ON Employee.id_user = "User".id_user
        WHERE "User".session_token = %s
        ''', (str(session_token),))
        user_type = cursor.fetchone()
        if user_type:
            return user_type['id_employee'], None
        return None, "Type utilisateur non trouvé"
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_user_role(user_id):
    """
    Récupère le rôle associé à un identifiant utilisateur donné depuis la base de données.

    Args:
        user_id (int): L'identifiant de l'utilisateur dont le rôle doit être récupéré.

    Returns:
        str: Le nom du rôle associé à l'utilisateur, ou None si une erreur est survenue ou si le rôle n'est pas trouvé.
    """
    conn = get_db_connection()
    if conn is None:
        print("Erreur base de données")
        return None
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
        SELECT Role.name_role
        FROM Role
        JOIN User_role ON Role.id_role = User_role.id_role
        WHERE User_role.id_user = %s
        ''', (user_id,))
        role = cursor.fetchone()
        if role:
            return role['name_role'], None
        else:
            return None, "Rôle non trouvé"
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None
    finally:
        conn.close()

def update_user_role(user_id, role_name):
    """
    Met à jour le rôle d'un utilisateur dans la base de données.

    Args:
        user_id (int): L'identifiant de l'utilisateur.
        role_name (str): Le nouveau rôle de l'utilisateur.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE User_role
        SET id_role = (SELECT id_role FROM Role WHERE name_role = %s)
        WHERE id_user = %s
        ''', (role_name, user_id))
        conn.commit()
        return None
    except psycopg2.Error as e:
        print(f"Erreur lors de la mise à jour du rôle de l'utilisateur: {e}")
        return "Erreur lors de la mise à jour du rôle de l'utilisateur"
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
        return None, "Erreur base de données"
    try:
        cursor = conn.cursor()

        # Insère l'utilisateur dans la table User
        cursor.execute('INSERT INTO "User" (username) VALUES (%s) RETURNING id_user', (email,))
        user_id = cursor.fetchone()[0]

        # Insere l'employé dans la base de données
        cursor.execute('INSERT INTO Employee (lastname_employee, name_employee, email_employee, id_user) VALUES (%s, %s, %s, %s) RETURNING id_employee', (lastname, name, email, user_id))
        employee_id = cursor.fetchone()[0]

        # Récupère l'id_role correspondant au nom du rôle
        cursor.execute('SELECT id_role FROM Role WHERE name_role = %s', (role,))
        role_id = cursor.fetchone()
        if role_id is None:
            return None, "Rôle non trouvé"

        # Insere l'association de l'employé avec le rôle dans la table User_role
        cursor.execute('INSERT INTO User_role (id_user, id_role) VALUES (%s, %s)', (user_id, role_id[0]))

        # Sauvegarde les modifications
        conn.commit()
        return employee_id, None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        cursor.execute('SELECT email_employee FROM Employee WHERE id_employee = %s', (id_employee,))
        employee = cursor.fetchone()
        return employee[0] if employee else None
    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Renvoie tous les employés de la base de données
        cursor.execute('''
        SELECT "User".id_user, "User".username, Employee.*, Role.name_role
        FROM Employee
        JOIN "User" ON Employee.id_user = "User".id_user
        JOIN User_role ON "User".id_user = User_role.id_user
        JOIN Role ON User_role.id_role = Role.id_role
        ''')
        employees = cursor.fetchall()
        if employees:
            return employees, None
        else:
            return None, "Pas d'employé"

    except psycopg2.Error as e:
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Exécute la requête pour récupérer l'employé
        cursor.execute('SELECT * FROM Employee WHERE id_employee = %s', (employee_id,))
        employee = cursor.fetchone()
        return employee, None
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        # Met à jour l'employé dans la base de données
        cursor.execute('UPDATE Employee SET lastname_employee = %s, name_employee = %s, email_employee = %s WHERE id_employee = %s', (lastname, name, email, id_employee))
        # Sauvegarde les modifications
        conn.commit()
    except psycopg2.Error as e:
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
        cursor = conn.cursor()
        # Supprime l'utilisateur associé à l'employé (employé supprimé en cascade)
        cursor.execute('DELETE FROM "User" WHERE id_user = (SELECT id_user FROM Employee WHERE id_employee = %s)', (id_employee,))
        # Sauvegarde les modifications
        conn.commit()
    except psycopg2.Error as e:
        # Gère les erreurs de requête SQL
        print(f"Erreur lors de la suppression de l'employé: {e}")
        return "Erreur lors de la suppression de l'employé"
    finally:
        # Ferme la connexion à la base de données
        conn.close()
    return None

# Feedback functions

def update_feedback(id_interview, feedback, type):
    """
    Met à jour le feedback d'un entretien dans la base de données.

    Args:
        id_interview (int): L'identifiant de l'entretien.
        feedback (str): Le feedback de l'entretien.
        type (str): Le type de feedback (candidat ou participant).

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"

    try:
        cursor = conn.cursor()
        if type == "candidate":
            cursor.execute('UPDATE Interview SET feedback_candidate = %s WHERE id_interview = %s', (feedback, id_interview))
        elif type == "participant":
            cursor.execute('UPDATE Interview SET feedback_participant = %s WHERE id_interview = %s', (feedback, id_interview))
        else:
            return "Type de feedback incorrect"
        conn.commit()
    except psycopg2.Error as e:
        print(f"Erreur lors de la mise à jour du feedback: {e}")
        return "Erreur lors de la mise à jour du feedback"
    finally:
        conn.close()
    return None