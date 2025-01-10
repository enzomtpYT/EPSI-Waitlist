import sqlite3
from lib.database import get_db_connection

# Candidate functions

def create_candidate(lastname, name, email):
    """
    Génère un candidat dans la base de données.

    Args:
        lastname (str): Le nom de famille du candidat.
        name (str): Le nom du candidat.
        email (str): L'adresse email du candidat.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        # Insere le candidat dans la base de données
        conn.execute('INSERT INTO Candidate (lastname_candidate, name_candidate, email_candidate) VALUES (?, ?, ?)', (lastname, name, email))
        # Sauvegarde les modifications
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la création du candidat: {e}")
        return "Erreur lors de la création du candidat"
    finally:
        # Fermes la connexion à la base de données
        conn.close()
    return None

def get_all_candidates():
    """
    Renvoie tous les candidats de la base de données.

    Returns:
        list: Une liste de dictionnaires représentant les candidats, ou None si une erreur est survenue.
        str: Un message d'erreur si une erreur est survenue, None sinon.
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
        dict: Un dictionnaire représentant le candidat, ou None si une erreur est survenue.
        str: Un message d'erreur si une erreur est survenue, None sinon.
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
        name (str): Le nom du candidat.
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
        id_candidate (int): L'identifiant du candidat à supprimer.

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
    Renvoie les entretiens d'un candidat à partir de son identifiant.

    Args:
        id_candidate (int): L'identifiant du candidat.

    Returns:
        list: Une liste de dictionnaires représentant les entretiens, ou None si une erreur est survenue.
        str: Un message d'erreur si une erreur est survenue, None sinon.
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
