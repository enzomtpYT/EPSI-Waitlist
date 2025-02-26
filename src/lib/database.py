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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        return conn, cursor
    except psycopg2.Error as e:
        print(f"Erreur base de données: {e}")
        return None, None

today = datetime.date.today()

def archive_schema(target_schema, source_schema="public"):
    """
    Copie les tables et les contraintes d'un schéma source vers un schéma cible.

    Args:
        target_schema (str): Le nom du schéma cible.
        source_schema="public" (str): Le nom du schéma source.

    Returns:
        str: Un message d'erreur si une erreur survient, None sinon.
    """
    # Connect to the PostgreSQL database
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"

    # Create the target schema
    cursor.execute(f"DROP SCHEMA IF EXISTS {target_schema} CASCADE;")
    cursor.execute(f"CREATE SCHEMA {target_schema};")

    # Copy tables from the source schema to the target schema
    cursor.execute(f"""
    DO $$
    DECLARE
        r RECORD;
        table_exists BOOLEAN;
    BEGIN
      -- Loop through all tables in the source schema and copy them to the target schema
      FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = '{source_schema}') LOOP
        -- Check if table already exists in the target schema
        SELECT EXISTS (
            SELECT 1
            FROM pg_tables
            WHERE schemaname = '{target_schema}'
            AND tablename = r.tablename
        ) INTO table_exists;

        -- If table does not exist in target schema, create it with data
        IF NOT table_exists THEN
            EXECUTE format('CREATE TABLE {target_schema}.%I AS TABLE {source_schema}.%I', r.tablename, r.tablename);
        END IF;
      END LOOP;

      -- Loop through constraints and copy them to the target schema
      FOR r IN (SELECT conname, conrelid::regclass AS tablename, pg_get_constraintdef(oid) AS condef
                FROM pg_constraint
                WHERE connamespace = (SELECT oid FROM pg_namespace WHERE nspname = '{source_schema}')) LOOP
        -- Ensure the table exists in the target schema before adding the constraint
        IF EXISTS (
            SELECT 1
            FROM pg_tables
            WHERE schemaname = '{target_schema}'
            AND tablename = r.tablename::text
        ) THEN
            EXECUTE format('ALTER TABLE "{target_schema}".%I ADD CONSTRAINT %I %s', r.tablename::text, r.conname, r.condef);
        END IF;
      END LOOP;
    END $$;
    """)

    # Commit the transaction after copying the schema
    conn.commit()

    # Drop constraints related to "User", "permission", "role", "user_role", and "role_permission" tables if they exist
    cursor.execute(f"""
    DO $$
    DECLARE
        r RECORD;
    BEGIN
        -- Drop foreign key constraints referencing "User" table
        IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = '{target_schema}' AND tablename = 'User') THEN
            FOR r IN (SELECT conname, conrelid::regclass AS tablename
                      FROM pg_constraint
                      WHERE confrelid = '{target_schema}."User"'::regclass) LOOP
                EXECUTE format('ALTER TABLE "{target_schema}".%I DROP CONSTRAINT %I', r.tablename, r.conname);
            END LOOP;
        END IF;

        -- Drop foreign key constraints referencing "permission" table
        IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = '{target_schema}' AND tablename = 'permission') THEN
            FOR r IN (SELECT conname, conrelid::regclass AS tablename
                      FROM pg_constraint
                      WHERE confrelid = '{target_schema}."permission"'::regclass) LOOP
                EXECUTE format('ALTER TABLE "{target_schema}".%I DROP CONSTRAINT %I', r.tablename, r.conname);
            END LOOP;
        END IF;

        -- Drop foreign key constraints referencing "role" table
        IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = '{target_schema}' AND tablename = 'role') THEN
            FOR r IN (SELECT conname, conrelid::regclass AS tablename
                      FROM pg_constraint
                      WHERE confrelid = '{target_schema}."role"'::regclass) LOOP
                EXECUTE format('ALTER TABLE "{target_schema}".%I DROP CONSTRAINT %I', r.tablename, r.conname);
            END LOOP;
        END IF;

        -- Drop foreign key constraints referencing "user_role" table
        IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = '{target_schema}' AND tablename = 'user_role') THEN
            FOR r IN (SELECT conname, conrelid::regclass AS tablename
                      FROM pg_constraint
                      WHERE confrelid = '{target_schema}."user_role"'::regclass) LOOP
                EXECUTE format('ALTER TABLE "{target_schema}".%I DROP CONSTRAINT %I', r.tablename, r.conname);
            END LOOP;
        END IF;

        -- Drop foreign key constraints referencing "role_permission" table
        IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = '{target_schema}' AND tablename = 'role_permission') THEN
            FOR r IN (SELECT conname, conrelid::regclass AS tablename
                      FROM pg_constraint
                      WHERE confrelid = '{target_schema}."role_permission"'::regclass) LOOP
                EXECUTE format('ALTER TABLE "{target_schema}".%I DROP CONSTRAINT %I', r.tablename, r.conname);
            END LOOP;
        END IF;
    END $$;
    """)

    # Delete the column id_user from the tables employee, candidate, and participant if they exist
    for table in ["employee", "candidate", "participant"]:
        cursor.execute(f"""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = '{target_schema}' AND tablename = '{table}') THEN
                EXECUTE 'ALTER TABLE {target_schema}."{table}" DROP COLUMN IF EXISTS id_user;';
            END IF;
        END $$;
        """)

    # Drop the "User", "permission", "role", "user_role", and "role_permission" tables
    cursor.execute(f"DROP TABLE IF EXISTS {target_schema}.\"User\" CASCADE;")
    cursor.execute(f"DROP TABLE IF EXISTS {target_schema}.\"permission\" CASCADE;")
    cursor.execute(f"DROP TABLE IF EXISTS {target_schema}.\"role\" CASCADE;")
    cursor.execute(f"DROP TABLE IF EXISTS {target_schema}.\"user_role\" CASCADE;")
    cursor.execute(f"DROP TABLE IF EXISTS {target_schema}.\"role_permission\" CASCADE;")

    # Commit the transaction and close the connection
    conn.commit()
    cursor.close()
    conn.close()
    return None

def wipe_candidates():
    """
    Supprime toutes les données de la table Candidate et toutes les données associées.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        # Supprime les données associées aux candidats dans les tables liées
        cursor.execute("DELETE FROM public.Candidate_tag WHERE id_candidate IN (SELECT id_candidate FROM public.Candidate)")
        cursor.execute("DELETE FROM public.Interview WHERE id_candidate IN (SELECT id_candidate FROM public.Candidate)")
        cursor.execute("DELETE FROM public.Attends WHERE id_candidate IN (SELECT id_candidate FROM public.Candidate)")

        # Supprime les candidats
        cursor.execute("DELETE FROM public.Candidate")

        # Supprime les utilisateurs associés aux candidats
        cursor.execute("DELETE FROM public.\"User\" WHERE id_user IN (SELECT id_user FROM public.Candidate)")

        # Supprime les événements
        cursor.execute("DELETE FROM public.Event")

        # Sauvegarde les modifications
        conn.commit()
        return None
    except psycopg2.Error as e:
        print(f"Erreur lors de la suppression des candidats: {e}")
        return "Erreur lors de la suppression des candidats"
    finally:
        conn.close()

def import_csv(jsoncsv):
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        for entry in jsoncsv:
            # Determine username
            username = entry['username'] if entry['username'] else entry['email']

            # Create or update user
            cursor.execute('''
            INSERT INTO "User" (username) VALUES (%s)
            ON CONFLICT (username) DO NOTHING RETURNING id_user
            ''', (username,))
            user_id = cursor.fetchone()
            if user_id is None:
                cursor.execute('SELECT id_user FROM "User" WHERE username = %s', (username,))
                user_id = cursor.fetchone()['id_user']
            else:
                user_id = user_id['id_user']

            # Create or update candidate
            cursor.execute('''
            INSERT INTO Candidate (lastname_candidate, name_candidate, email_candidate, id_user)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email_candidate) DO NOTHING RETURNING id_candidate
            ''', (entry['lastname'], entry['name'], entry['email'], user_id))
            candidate_id = cursor.fetchone()
            if candidate_id is None:
                cursor.execute('SELECT id_candidate FROM Candidate WHERE email_candidate = %s', (entry['email'],))
                candidate_id = cursor.fetchone()['id_candidate']
            else:
                candidate_id = candidate_id['id_candidate']

            # Create or update tags
            for tag_name in entry['tags']:
                cursor.execute('''
                INSERT INTO Tag (name_tag) VALUES (%s)
                ON CONFLICT (name_tag) DO NOTHING RETURNING id_tag
                ''', (tag_name,))
                tag_id = cursor.fetchone()
                if tag_id is None:
                    cursor.execute('SELECT id_tag FROM Tag WHERE name_tag = %s', (tag_name,))
                    tag_id = cursor.fetchone()['id_tag']
                else:
                    tag_id = tag_id['id_tag']

                # Associate tag with candidate
                cursor.execute('''
                INSERT INTO Candidate_tag (id_candidate, id_tag) VALUES (%s, %s)
                ON CONFLICT (id_candidate, id_tag) DO NOTHING
                ''', (candidate_id, tag_id))

        conn.commit()
        return None
    except psycopg2.Error as e:
        print(f"Erreur lors de l'importation des données CSV: {e}")
        return "Erreur lors de l'importation des données CSV"
    finally:
        conn.close()

def get_archived_schemas():
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor.execute('''
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name = 'public' OR schema_name LIKE 'archive_%'
        ''')
        schemas = [row['schema_name'] for row in cursor.fetchall()]

        result = []
        for schema in schemas:
            cursor.execute(f'''
            SELECT Candidate.*, json_agg(DISTINCT Tag.*) AS tags, json_agg(DISTINCT Interview.*) AS interviews
            FROM {schema}.Candidate
            LEFT JOIN {schema}.Candidate_tag ON Candidate.id_candidate = Candidate_tag.id_candidate
            LEFT JOIN {schema}.Tag ON Candidate_tag.id_tag = Tag.id_tag
            LEFT JOIN {schema}.Interview ON Candidate.id_candidate = Interview.id_candidate
            GROUP BY Candidate.id_candidate
            ''')
            candidates = cursor.fetchall()
            for candidate in candidates:
                if candidate['interviews']:
                    for interview in candidate['interviews']:
                        if interview:
                            # Event info
                            cursor.execute(f'''
                            SELECT Event.*
                            FROM {schema}.Event
                            WHERE Event.id_event = %s
                            ''', (interview['id_event'],))
                            event = cursor.fetchone()
                            interview['event'] = event
                            # Participant
                            cursor.execute(f'''
                            SELECT Participant.*
                            FROM {schema}.Participant
                            JOIN {schema}.Interview ON Participant.id_participant = Interview.id_participant
                            WHERE Interview.id_interview = %s
                            ''', (interview['id_interview'],))
                            participant = cursor.fetchone()
                            interview['participant'] = participant
            result.append({
                'schema_name': schema,
                'candidates': candidates
            })
        return result, None
    except psycopg2.Error as e:
        print(f"Erreur lors de la récupération des schémas archivés: {e}")
        return None, "Erreur lors de la récupération des schémas archivés"
    finally:
        conn.close()

# Event functions

def create_event(name, date, has_timeslots=False, start_time_event=None, end_time_event=None, tags=[]):
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
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor.execute('INSERT INTO Event (name_event, date_event, has_timeslots, start_time_event, end_time_event) VALUES (%s, %s, %s, %s, %s) RETURNING id_event', (name, date, has_timeslots, start_time_event, end_time_event))
        event_id = cursor.fetchone()['id_event']
        if tags:
            for tag in tags:
                cursor.execute('INSERT INTO Event_tag (id_event, id_tag) VALUES (%s, %s)', (event_id, tag['id_tag']))
        return event_id, None
    except psycopg2.Error as e:
        print(f"Erreur lors de la création de l'événement: {e}")
        return None, "Erreur lors de la création de l'événement"
    finally:
        conn.close()

def get_all_events():
    """
    Récupère tous les événements de la base de données et ajoute les tags associés à chaque événement.

    Returns:
        list: Une liste de dictionnaires représentant les événements.
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor.execute('SELECT * FROM Event')
        events = cursor.fetchall()
        if events:
            for event in events:
                # Get tags
                cursor.execute('''
                SELECT Tag.*
                FROM Tag
                JOIN Event_tag ON Tag.id_tag = Event_tag.id_tag
                WHERE Event_tag.id_event = %s
                ''', (event['id_event'],))
                tags = cursor.fetchall()
                event['tags'] = tags
                # Get Interviews
                cursor.execute('''
                SELECT Interview.*, Participant.name_participant, Candidate.lastname_candidate, Candidate.name_candidate
                FROM Interview
                JOIN Participant ON Interview.id_participant = Participant.id_participant
                JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate
                WHERE Interview.id_event = %s
                ''', (event['id_event'],))
                interviews = cursor.fetchall()
                event['interviews'] = interviews
            return events, None
        else:
            return [], None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_event(event_id):
    """
    Récupère un événement de la base de données en utilisant son identifiant et inclut les créneaux horaires et les tags associés.

    Args:
        event_id (int): L'identifiant de l'événement.

    Returns:
        dict: Un dictionnaire représentant l'événement, ses créneaux horaires et ses tags.
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor.execute('SELECT * FROM Event WHERE id_event = %s', (event_id,))
        event = cursor.fetchone()
        event = dict(event)
        if event['has_timeslots']:
            cursor.execute('SELECT * FROM Timeslot WHERE id_event = %s', (event_id,))
            timeslots = cursor.fetchall()
            event['timeslots'] = timeslots
        cursor.execute('''
        SELECT Tag.id_tag, Tag.name_tag
        FROM Tag
        JOIN Event_tag ON Tag.id_tag = Event_tag.id_tag
        WHERE Event_tag.id_event = %s
        ''', (event_id,))
        tags = cursor.fetchall()
        event['tags'] = [dict(tag) for tag in tags]
        # Add event interviews
        cursor.execute('''
        SELECT Interview.*, Participant.name_participant, Candidate.lastname_candidate, Candidate.name_candidate
        FROM Interview
        JOIN Participant ON Interview.id_participant = Participant.id_participant
        JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate
        WHERE Interview.id_event = %s
        ''', (event_id,))
        interviews = cursor.fetchall()
        event['interviews'] = interviews
        return event, None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def edit_event(name, date, id_event, has_timeslots=False, start_time_event=None, end_time_event=None):
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
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor.execute('UPDATE Event SET name_event = %s, date_event = %s, has_timeslots = %s, start_time_event = %s, end_time_event = %s WHERE id_event = %s', (name, date, has_timeslots, start_time_event, end_time_event, id_event))
    except psycopg2.Error as e:
        print(f"Erreur lors de la mise à jour de l'événnement: {e}")
        return "Erreur lors de la mise à jour de l'événnement"
    finally:
        conn.close()
    return None

def add_timeslot_to_event(id_event, start_timeslot, end_timeslot, nbr_spots):
    """
    Ajoute des créneaux horaires à un événement.

    Args:
        id_event (int): L'identifiant de l'événement.
        start_timeslot (str): L'heure de début du créneau horaire.
        end_timeslot (str): L'heure de fin du créneau horaire.
        nbr_spots (int): Le nombre de places disponibles.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor.execute('''
        INSERT INTO Timeslot (id_event, start_timeslot, end_timeslot, nbr_spots_timeslot)
        VALUES (%s, %s, %s, %s)
        ''', (id_event, start_timeslot, end_timeslot, nbr_spots))
        conn.commit()
        return None
    except psycopg2.Error as e:
        print(f"Erreur lors de l'ajout des créneaux horaires: {e}")
        return "Erreur lors de l'ajout des créneaux horaires"
    finally:
        conn.close()

def edit_timeslot(start_timeslot, end_timeslot, nbr_spots, id_timeslot):
    """
    Modifie le créneau horaires d'un événement.

    Args:
        id_event (int): L'identifiant de l'événement.
        start_timeslot (str): L'heure de début du créneau horaire.
        end_timeslot (str): L'heure de fin du créneau horaire.
        nbr_spots (int): Le nombre de places disponibles.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor.execute('''
        UPDATE Timeslot SET start_timeslot = %s, end_timeslot = %s, nbr_spots_timeslot = %s WHERE id_timeslot = %s
        ''', (start_timeslot, end_timeslot, nbr_spots, id_timeslot))
        conn.commit()
        return None
    except psycopg2.Error as e:
        print(f"Erreur lors de l'ajout des créneaux horaires: {e}")
        return "Erreur lors de l'ajout des créneaux horaires"
    finally:
        conn.close()

def delete_timeslot(id_timeslot):
    """
    Supprime un événement de la base de données en utilisant son identifiant.

    Args:
        id_timeslot (int): L'identifiant de l'événement.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor.execute("DELETE FROM Timeslot WHERE id_timeslot = %s", (id_timeslot,))
        conn.commit()
        return None
    except psycopg2.Error as e:
        print(f"Erreur lors de la suppression de l'événement: {e}")
        return "Erreur lors de la suppression de l'événement"
    finally:
        conn.close()

def delete_event(id_event):
    """
    Supprime un événement de la base de données en utilisant son identifiant.

    Args:
        id_event (int): L'identifiant de l'événement.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor.execute("DELETE FROM Event WHERE id_event = %s", (id_event,))
    except psycopg2.Error as e:
        print(f"Erreur lors de la suppression de l'événement: {e}")
        return "Erreur lors de la suppression de l'événement"
    finally:
        conn.close()
    return None

def get_today_events():
    """
    Récupère les événements prévus pour aujourd'hui.

    Returns:
        tuple: Un tuple contenant l'identifiant de l'événement et un message d'erreur si une erreur est survenue.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor.execute('SELECT id_event FROM Event WHERE date_event = %s', (today,))
        events = cursor.fetchall()
        if events:
            return events['id_event'], None
        else:
            return None, "Pas d'événement aujourd'hui"
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_event_candidates(id_event):
    """
    Récupère les candidats associés à un événement.

    Args:
        id_event (int): L'identifiant de l'événement.

    Returns:
        tuple: Un tuple contenant une liste de candidats et un message d'erreur si une erreur est survenue.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor.execute('''
        SELECT Candidate.*, Attends.priority
        FROM Candidate
        JOIN Attends ON Candidate.id_candidate = Attends.id_candidate
        WHERE Attends.id_event = %s
        ''', (id_event,))
        candidates = cursor.fetchall()
        return candidates, None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_event_participants(id_event):
    """
    Récupère les participants associés à un événement.

    Args:
        id_event (int): L'identifiant de l'événement.

    Returns:
        tuple: Un tuple contenant une liste de participants et un message d'erreur si une erreur est survenue.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor.execute('''
        SELECT Participant.*
        FROM Participant
        JOIN Participates ON Participant.id_participant = Participates.id_participant
        WHERE Participates.id_event = %s
        ''', (id_event,))
        participants = cursor.fetchall()
        return participants, None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def upsert_event_attends(id_event, id_candidate, priority):
    """
    Insère ou met à jour un candidat dans la table Attends.

    Args:
        id_event (int): L'identifiant de l'événement.
        id_candidate (int): L'identifiant du candidat.
        priority (int): La priorité du candidat.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor.execute('''
        INSERT INTO Attends (id_event, id_candidate, priority)
        VALUES (%s, %s, %s)
        ON CONFLICT (id_event, id_candidate) DO UPDATE SET priority = %s
        ''', (id_event, id_candidate, priority, priority))
        conn.commit()
        return None
    except psycopg2.Error as e:
        print(f"Erreur lors de l'insertion ou de la mise à jour du candidat: {e}")
        return "Erreur lors de l'insertion ou de la mise à jour du candidat"
    finally:
        conn.close()

def upsert_event_participates(id_event, id_participant):
    """
    Insère ou met à jour un participant dans la table Participates.

    Args:
        id_event (int): L'identifiant de l'événement.
        id_participant (int): L'identifiant du participant.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor.execute('''
        INSERT INTO Participates (id_event, id_participant)
        VALUES (%s, %s)
        ON CONFLICT (id_event, id_participant) DO NOTHING
        ''', (id_event, id_participant))
        conn.commit()
        return None
    except psycopg2.Error as e:
        print(f"Erreur lors de l'insertion ou de la mise à jour du participant: {e}")
        return "Erreur lors de l'insertion ou de la mise à jour du participant"
    finally:
        conn.close()

def get_event_details(id_event):
    """
    Récupère les détails d'un événement, y compris les candidats, les participants et les tags associés.

    Args:
        id_event (int): L'identifiant de l'événement.

    Returns:
        dict: Un dictionnaire contenant les détails de l'événement, les candidats, les participants et les tags.
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:

        # Récupère les informations de l'événement et les tags associés en une seule requête
        cursor.execute('''
        SELECT Event.*,
               COALESCE(json_agg(DISTINCT Tag.*) FILTER (WHERE Tag.id_tag IS NOT NULL), '[]') AS tags
        FROM Event
        LEFT JOIN Event_tag ON Event.id_event = Event_tag.id_event
        LEFT JOIN Tag ON Event_tag.id_tag = Tag.id_tag
        WHERE Event.id_event = %s
        GROUP BY Event.id_event
        ''', (id_event,))
        event = cursor.fetchone()
        # Convert datetime.time objects to strings
        if event:
            if 'start_time_event' in event and isinstance(event['start_time_event'], datetime.time):
                event['start_time_event'] = event['start_time_event'].strftime('%H:%M:%S')
            if 'end_time_event' in event and isinstance(event['end_time_event'], datetime.time):
                event['end_time_event'] = event['end_time_event'].strftime('%H:%M:%S')

        # Récupère tous les candidats et leurs tags en une seule requête
        cursor.execute('''
        SELECT Candidate.*,
               COALESCE(json_agg(DISTINCT Tag.*) FILTER (WHERE Tag.id_tag IS NOT NULL), '[]') AS tags,
               COALESCE(Attends.priority, 1) AS priority,
               COALESCE(Attends.id_event IS NOT NULL, FALSE) AS attends
        FROM Candidate
        LEFT JOIN Candidate_tag ON Candidate.id_candidate = Candidate_tag.id_candidate
        LEFT JOIN Tag ON Candidate_tag.id_tag = Tag.id_tag
        LEFT JOIN Attends ON Candidate.id_candidate = Attends.id_candidate AND Attends.id_event = %s
        GROUP BY Candidate.id_candidate, Attends.priority, Attends.id_event
        ''', (id_event,))
        all_candidates = cursor.fetchall()

        # Récupère tous les participants et leurs tags en une seule requête
        cursor.execute('''
        SELECT Participant.*,
               COALESCE(json_agg(DISTINCT Tag.*) FILTER (WHERE Tag.id_tag IS NOT NULL), '[]') AS tags,
               COALESCE(Participates.id_event IS NOT NULL, FALSE) AS attends
        FROM Participant
        LEFT JOIN Participant_tag ON Participant.id_participant = Participant_tag.id_participant
        LEFT JOIN Tag ON Participant_tag.id_tag = Tag.id_tag
        LEFT JOIN Participates ON Participant.id_participant = Participates.id_participant AND Participates.id_event = %s
        GROUP BY Participant.id_participant, Participates.id_event
        ''', (id_event,))
        all_participants = cursor.fetchall()

        # Récupère tous les tags
        cursor.execute('SELECT * FROM Tag')
        all_tags = cursor.fetchall()

        return {
            "event": event,
            "candidates": all_candidates,
            "participants": all_participants,
            "tags": all_tags
        }, None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def get_event_interview_candidate(todayevent, id_participant, happened=None):
    """
    Récupère les candidats associés aux interviews d'un participant pour un événement.

    Args:
        todayevent (int): L'identifiant de l'événement.
        id_participant (int): L'identifiant du participant.

    Returns:
        tuple: Un tuple contenant une liste de candidats et un message d'erreur si une erreur est survenue.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        if happened is None:
            cursor.execute('''
            SELECT Interview.id_interview, Interview.id_candidate, Interview.id_participant, Interview.start_time_interview, Candidate.lastname_candidate, Candidate.name_candidate, Attends.priority
            FROM Interview
            JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate
            JOIN Attends ON Interview.id_event = Attends.id_event AND Interview.id_candidate = Attends.id_candidate
            WHERE Interview.id_event = %s AND id_participant = %s
            ''', (todayevent, id_participant))
        else:
            cursor.execute('''
            SELECT Interview.id_interview, Interview.id_candidate, Interview.id_participant, Interview.start_time_interview, Candidate.lastname_candidate, Candidate.name_candidate, Attends.priority
            FROM Interview
            JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate
            JOIN Attends ON Interview.id_event = Attends.id_event AND Interview.id_candidate = Attends.id_candidate
            WHERE Interview.id_event = %s AND id_participant = %s AND happened = %s
            ''', (todayevent, id_participant, happened))
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
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:

        # Insère l'utilisateur dans la table User
        cursor.execute('INSERT INTO "User" (username) VALUES (%s) RETURNING id_user', (email,))
        user_id = cursor.fetchone()['id_user']

        # Insere le candidat dans la base de données
        cursor.execute('INSERT INTO Candidate (lastname_candidate, name_candidate, email_candidate, id_user) VALUES (%s, %s, %s, %s) RETURNING id_candidate', (lastname, name, email, user_id))
        candidate_id = cursor.fetchone()['id_candidate']

        # Assigne le rôle "candidate" à l'utilisateur
        cursor.execute('INSERT INTO User_role (id_user, id_role) VALUES (%s, (SELECT id_role FROM Role WHERE name_role = %s))', (user_id, 'candidate'))

        # Sauvegarde les modifications
        conn.commit()
        return candidate_id, user_id, None
    except psycopg2.Error as e:
        print(f"Erreur lors de la création du candidat: {e}")
        return None, "Erreur lors de la création du candidat"
    finally:
        # Fermes la connexion à la base de données
        conn.close()

def get_all_candidates():
    """
    Récupère tous les candidats de la base de données.

    Args:
        schema (str): Le schéma de la base de données à utiliser.

    Returns:
        tuple: Un tuple contenant une liste de candidats et un message d'erreur si une erreur est survenue.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"

    try:
        cursor.execute(f'SELECT * FROM Candidate')
        candidates = cursor.fetchall()

        if candidates:
            return candidates, None
        else:
            return [], None

    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"

    finally:
        # Ferme la connexion à la base de données
        conn.close()

def get_candidate(candidate_id):
    """
    Récupère un candidat de la base de données en utilisant son identifiant.

    Args:
        candidate_id (int): L'identifiant du candidat.

    Returns:
        tuple: Un tuple contenant le candidat et un message d'erreur si une erreur est survenue.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        # Si la connexion échoue, renvoie une erreur
        return None, "Erreur base de données"
    try:
        cursor.execute('''
        SELECT Candidate.*, "User".username
        FROM Candidate
        JOIN "User" ON Candidate.id_user = "User".id_user
        WHERE id_candidate = %s
        ''', (candidate_id,))
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
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"

    try:
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
    conn, cursor = get_db_connection()
    if conn is None:
        # Si la connexion échoue, renvoie une erreur
        return "Erreur base de données"
    try:
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
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"

    try:
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
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"

    try:
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
    conn, cursor = get_db_connection()
    if conn is None:
        # Si la connexion échoue, renvoie une erreur
        return None, "Erreur base de données"
    try:
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
    conn, cursor = get_db_connection()
    if conn is None:
        # Si la connexion échoue, renvoie une erreur
        return "Erreur base de données"
    try:
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

def delete_candidate_from_event(id_event, id_candidate):
    """
    Supprime un candidat d'un événement.

    Args:
        id_event (int): L'identifiant de l'événement.
        id_candidate (int): L'identifiant du candidat.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        # Si la connexion échoue, renvoie une erreur
        return "Erreur base de données"
    try:
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
    conn, cursor = get_db_connection()
    if conn is None:
        return None, None, "Erreur base de données"
    try:

        # Insère l'utilisateur dans la table User
        cursor.execute('INSERT INTO "User" (username) VALUES (%s) RETURNING id_user', (email,))
        user_id = cursor.fetchone()['id_user']

        # Insere l'intervenant dans la base de données
        cursor.execute('INSERT INTO Participant (name_participant, email_participant, id_user) VALUES (%s, %s, %s) RETURNING id_participant', (name, email, user_id))
        participant_id = cursor.fetchone()['id_participant']

        # Assigne le rôle "participant" à l'utilisateur
        cursor.execute('INSERT INTO User_role (id_user, id_role) VALUES (%s, (SELECT id_role FROM Role WHERE name_role = %s))', (user_id, 'participant'))

        # Sauvegarde les modifications
        conn.commit()
        return participant_id, user_id, None
    except psycopg2.Error as e:
        print(f"Erreur lors de la création de l'intervenant: {e}")
        return None, None, "Erreur lors de la création de l'intervenant"
    finally:
        # Fermes la connexion à la base de données
        conn.close()

def get_all_participants():
    """
    Récupère tous les participants de la base de données.

    Returns:
        tuple: Un tuple contenant une liste de participants et un message d'erreur si une erreur est survenue.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor.execute('SELECT * FROM Participant')
        participants = cursor.fetchall()
        if participants:
            return participants, None
        else:
            return [], None
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
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor.execute('''
        SELECT Participant.*, "User".username
        FROM Participant
        JOIN "User" ON Participant.id_user = "User".id_user
        WHERE id_participant = %s
        ''', (participant_id,))
        participant = cursor.fetchone()
        return participant, None
    except psycopg2.Error as e:
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
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
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
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
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
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
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
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
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

# Interview functions

def get_user_past_interviews(session_token):
    """
    Récupère les entretiens passés d'un utilisateur.

    Args:
        session_token (str): Le token de session de l'utilisateur.

    Returns:
        tuple: Un tuple contenant une liste d'entretiens et un message d'erreur si une erreur est survenue.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
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
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor.execute('''
        INSERT INTO Interview (id_event, id_participant, id_candidate, happened)
        VALUES (%s, %s, %s, FALSE)
        ON CONFLICT ON CONSTRAINT interview_unique_constraint DO NOTHING
        ''', (id_event, id_participant, id_candidate))
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
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor.execute('SELECT * FROM Interview WHERE id_interview = %s', (id_interview,))
        interview = cursor.fetchone()
        return interview, None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def editstart_interview(id_interview, start_time):
    """
    Démarre un entretien en enregistrant l'heure de début.

    Args:
        id_interview (int): L'identifiant de l'entretien.
        start_time (datetime): L'heure de début de l'entretien.

    Returns:
        tuple: Un tuple contenant l'identifiant de l'entretien, l'événement associé et un message d'erreur si une erreur est survenue.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return None, None, "Erreur base de données"
    try:
        cursor.execute('''
        UPDATE Interview
        SET start_time_interview = %s
        WHERE id_interview = %s
        RETURNING id_interview, id_event
        ''', (start_time, id_interview))
        conn.commit()
        updated_ids = cursor.fetchone()
        return updated_ids['id_interview'], updated_ids['id_event'], None
    except psycopg2.Error as e:
        print(f"Erreur lors du démarrage de l'entretien: {e}")
        return None, None, "Erreur lors du démarrage de l'entretien"
    finally:
        conn.close()

def end_interview(interview_id, status):
    """
    Termine un entretien en enregistrant l'heure de fin et en calculant la durée.

    Args:
        id_interview (int): L'identifiant de l'entretien.

    Returns:
        tuple: Un tuple contenant l'identifiant de l'événement et un message d'erreur si une erreur est survenue.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        end_time = datetime.datetime.now()
        cursor.execute('''
        UPDATE Interview
        SET happened = %s, end_time_interview = %s, duration_interview = %s - start_time_interview
        WHERE id_interview = %s
        RETURNING id_event
        ''', (status, end_time, end_time, interview_id))
        event_id = cursor.fetchone()['id_event']
        conn.commit()
        return event_id, None
    except psycopg2.Error as e:
        print(f"Erreur lors de la fin de l'entretien: {e}")
        return None, "Erreur lors de la fin de l'entretien"
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
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor.execute("DELETE FROM Interview WHERE id_interview = %s", (id_interview,))
        conn.commit()
    except psycopg2.Error as e:
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
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
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
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor.execute('SELECT * FROM Tag')
        tags = cursor.fetchall()
        if tags:
            return tags, None
        else:
            return [], None
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
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
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
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
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
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
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
    conn, cursor = get_db_connection()
    try:
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
    conn, cursor = get_db_connection()
    try:
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
    conn, cursor = get_db_connection()
    try:
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
    conn, cursor = get_db_connection()
    try:
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
    conn, cursor = get_db_connection()
    try:
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
    conn, cursor = get_db_connection()
    try:
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
    conn, cursor = get_db_connection()
    try:
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
    conn, cursor = get_db_connection()
    try:
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
    conn, cursor = get_db_connection()
    try:
        cursor.execute('DELETE FROM Event_tag WHERE id_event = %s AND id_tag = %s', (id_event, id_tag))
        conn.commit()
        return None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return "Erreur requête base de données"
    finally:
        conn.close()

# Attends and Participates functions

def delete_attends(id_candidate, id_event):
    """
    Supprime une participation de la base de données en utilisant l'identifiant du candidat et de l'événement.

    Args:
        id_candidate (int): L'identifiant du candidat.
        id_event (int): L'identifiant de l'événement.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor.execute("DELETE FROM Attends WHERE id_candidate = %s AND id_event = %s", (id_candidate, id_event))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Erreur lors de la suppression de la participation: {e}")
        return "Erreur lors de la suppression de la participation"
    finally:
        conn.close()
    return None

def delete_participates(id_event, id_participant):
    """
    Supprime une participation de la base de données en utilisant l'identifiant du participant et de l'événement.

    Args:
        id_participant (int): L'identifiant du participant.
        id_event (int): L'identifiant de l'événement.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
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
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor.execute('SELECT session_token FROM "User" WHERE username = %s', (username,))
        session = cursor.fetchone()
        return session['session_token'], None
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
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
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
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor.execute('UPDATE "User" SET password_user = %s, session_token = %s WHERE username = %s', (password, session_token, username))
        conn.commit()
        return None
    except psycopg2.Error as e:
        print(f"Erreur lors de la mise à jour du mot de passe de l'utilisateur: {e}")
        return "Erreur lors de la mise à jour du mot de passe de l'utilisateur"
    finally:
        conn.close()

def auth_update_password(password, session_token, id_user):
    """
    Met à jour le mot de passe d'un utilisateur dans la base de données.

    Args:
        password (str): Le mot de passe hashé de l'utilisateur.
        session_token (str): Le jeton de session de l'utilisateur.
        id_user (int): L'identifiant de l'utilisateur.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor.execute('UPDATE "User" SET password_user = %s, session_token = %s WHERE id_user = %s', (password, session_token, id_user))
        conn.commit()
        return None
    except psycopg2.Error as e:
        print(f"Erreur lors de la mise à jour du mot de passe de l'utilisateur: {e}")
        return "Erreur lors de la mise à jour du mot de passe de l'utilisateur"
    finally:
        conn.close()

def auth_update_username(username, id_user):
    """
    Met à jour le nom d'utilisateur d'un utilisateur dans la base de données.

    Args:
        username (str): Le nom d'utilisateur de l'utilisateur.
        id_user (int): L'identifiant de l'utilisateur.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor.execute('UPDATE "User" SET username = %s WHERE id_user = %s', (username, id_user))
        conn.commit()
        return None
    except psycopg2.Error as e:
        print(f"Erreur lors de la mise à jour du nom d'utilisateur de l'utilisateur: {e}")
        return "Erreur lors de la mise à jour du nom d'utilisateur de l'utilisateur"
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
    conn, cursor = get_db_connection()
    try:
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
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor.execute('''
        SELECT Role.name_role
        FROM Role
        JOIN User_role ON Role.id_role = User_role.id_role
        JOIN "User" ON User_role.id_user = "User".id_user
        WHERE "User".session_token = %s
        ''', (session_token,))
        role = cursor.fetchone()
        if role:
            return role['name_role'], None
        else:
            return None, "Rôle non trouvé"
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
    conn, cursor = get_db_connection()
    try:
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
    conn, cursor = get_db_connection()
    try:
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
    conn, cursor = get_db_connection()
    try:
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
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
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
    conn, cursor = get_db_connection()
    if conn is None:
        print("Erreur base de données")
        return None
    try:
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

def get_profile_info(session_token):
    """
    Récupère les informations de profil d'un utilisateur

    Args:
        session_token (str): Le jeton de session de l'utilisateur.


    Returns:
        tuple: Un tuple contenant les informations de profil (nom d'utilisateur, email, (plus tard: CV, biographie), type d'utilisateur (particpant, candidat, etc..) et un message d'erreur si une erreur est survenue.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor.execute('''
        SELECT "User".username, Candidate.email_candidate AS email
        FROM "User"
        JOIN Candidate ON "User".id_user = Candidate.id_user
        WHERE "User".session_token = %s
        ''', (session_token,))
        candidate = cursor.fetchone()
        if candidate:
            candidate['type'] = "candidate"
            return candidate, None
        cursor.execute('''
        SELECT "User".username, Participant.email_participant AS email
        FROM "User"
        JOIN Participant ON "User".id_user = Participant.id_user
        WHERE "User".session_token = %s
        ''', (session_token,))
        participant = cursor.fetchone()
        if participant:
            participant['type'] = "participant"
            return participant, None
        cursor.execute('''
        SELECT "User".username, Employee.email_employee AS email
        FROM "User"
        JOIN Employee ON "User".id_user = Employee.id_user
        WHERE "User".session_token = %s
        ''', (session_token,))
        employee = cursor.fetchone()
        if employee:
            employee['type'] = "employee"
            return employee, None
        return None, "Profil non trouvé"
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

def update_profile_info(oldusername, newusername, email):
    """
    Met à jour les informations de profil d'un utilisateur

    Args:
        oldusername (str): L'ancien nom d'utilisateur de l'utilisateur.
        newusername (str): Le nouveau nom d'utilisateur de l'utilisateur.
        email (str): L'email de l'utilisateur.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:
        cursor.execute('''
        UPDATE "User"
        SET username = %s
        WHERE username = %s
        ''', (newusername, oldusername))
        conn.commit()
        cursor.execute('''
        UPDATE Candidate
        SET email_candidate = %s
        WHERE id_user = (SELECT id_user FROM "User" WHERE username = %s)
        ''', (email, newusername))
        conn.commit()
        cursor.execute('''
        UPDATE Participant
        SET email_participant = %s
        WHERE id_user = (SELECT id_user FROM "User" WHERE username = %s)
        ''', (email, newusername))
        conn.commit()
        return None
    except psycopg2.Error as e:
        print(f"Erreur lors de la mise à jour des informations de profil: {e}")
        return "Erreur lors de la mise à jour des informations de profil"
    finally:
        conn.close()

def get_user(user_id):
    """
    Récupère un utilisateur de la base de données en utilisant son identifiant.

    Args:
        user_id (int): L'identifiant de l'utilisateur.

    Returns:
        tuple: Un tuple contenant l'utilisateur et un message d'erreur si une erreur est survenue.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor.execute('SELECT * FROM "User" WHERE id_user = %s', (user_id,))
        user = cursor.fetchone()
        return user, None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
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
    conn, cursor = get_db_connection()
    if conn is None:
        return None, None, "Erreur base de données"
    try:

        # Insère l'utilisateur dans la table User
        cursor.execute('INSERT INTO "User" (username) VALUES (%s) RETURNING id_user', (email,))
        user_id = cursor.fetchone()['id_user']

        # Insere l'employé dans la base de données
        cursor.execute('INSERT INTO Employee (lastname_employee, name_employee, email_employee, id_user) VALUES (%s, %s, %s, %s) RETURNING id_employee', (lastname, name, email, user_id))
        employee_id = cursor.fetchone()['id_employee']

        # Récupère l'id_role correspondant au nom du rôle
        cursor.execute('SELECT id_role FROM Role WHERE name_role = %s', (role,))
        role_id = cursor.fetchone()
        if role_id is None:
            return None, None, "Rôle non trouvé"

        # Insere l'association de l'employé avec le rôle dans la table User_role
        cursor.execute('INSERT INTO User_role (id_user, id_role) VALUES (%s, %s)', (user_id, role_id['id_role']))

        # Sauvegarde les modifications
        conn.commit()
        return employee_id, user_id, None
    except psycopg2.Error as e:
        print(f"Erreur lors de la création de l'employé: {e}")
        return None, None, "Erreur lors de la création de l'employé"
    finally:
        # Ferme la connexion à la base de données
        conn.close()

def get_all_employees():
    """
    Récupère tous les employés de la base de données.

    Returns:
        tuple: Un tuple contenant une liste d'employés et un message d'erreur si une erreur est survenue.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"

    try:
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
            return [], None

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
    conn, cursor = get_db_connection()
    if conn is None:
        # Si la connexion échoue, renvoie une erreur
        return None, "Erreur base de données"
    try:
        # Exécute la requête pour récupérer l'employé et le nom d'utilisateur
        cursor.execute('''
        SELECT Employee.*, "User".username
        FROM Employee
        JOIN "User" ON Employee.id_user = "User".id_user
        WHERE id_employee = %s
        ''', (employee_id,))
        employee = cursor.fetchone()
        return employee, None
    except psycopg2.Error as e:
        # Gère les erreurs de requête SQL
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        # Ferme la connexion à la base de données
        conn.close()

def edit_employee(lastname, name, email, role, id_employee):
    """
    Met à jour les informations d'un employé, y compris son rôle.

    Args:
        lastname (str): Le nom de famille de l'employé.
        name (str): Le prénom de l'employé.
        email (str): L'adresse email de l'employé.
        role (str): Le rôle de l'employé.
        id_employee (int): L'identifiant de l'employé.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"
    try:

        # Met à jour les informations de l'employé dans la table Employee
        cursor.execute('''
        UPDATE Employee
        SET lastname_employee = %s, name_employee = %s, email_employee = %s
        WHERE id_employee = %s
        ''', (lastname, name, email, id_employee))

        # Récupère l'id_role correspondant au nom du rôle
        cursor.execute('SELECT id_role FROM Role WHERE name_role = %s', (role,))
        role_id = cursor.fetchone()
        if role_id is None:
            return "Rôle non trouvé"

        # Met à jour le rôle de l'utilisateur dans la table User_role
        cursor.execute('''
        UPDATE User_role
        SET id_role = %s
        WHERE id_user = (SELECT id_user FROM Employee WHERE id_employee = %s)
        ''', (role_id['id_role'], id_employee))

        conn.commit()
        return None
    except psycopg2.Error as e:
        print(f"Erreur lors de la mise à jour de l'employé: {e}")
        return "Erreur lors de la mise à jour de l'employé"
    finally:
        conn.close()

def delete_employee(id_employee):
    """
    Supprime un employé de la base de données en utilisant son identifiant.

    Args:
        id_employee (int): L'identifiant de l'employé.

    Returns:
        str: Un message d'erreur si une erreur est survenue, None sinon.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        # Si la connexion échoue, renvoie une erreur
        return "Erreur base de données"
    try:
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

def get_employee_interviews(id_employee):
    """
    Récupère les interviews associées à un employée.

    Args:
        id_employee (int): L'identifiant du employée.

    Returns:
        tuple: Un tuple contenant une liste d'interviews et un message d'erreur si une erreur est survenue.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor.execute('''
        SELECT Interview.id_interview, Event.name_event, Event.date_event, Candidate.lastname_candidate, Candidate.name_candidate, Interview.feedback_employee, Interview.feedback_candidate, Interview.duration_interview
        FROM Interview
        JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate
        JOIN Employee ON Interview.id_employee = Employee.id_employee
        JOIN Event ON Interview.id_event = Event.id_event
        WHERE Interview.id_employee = %s AND Interview.happened = TRUE
        ''', (id_employee,))
        interviews = cursor.fetchall()
        return interviews, None
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"
    finally:
        conn.close()

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
    conn, cursor = get_db_connection()
    if conn is None:
        return "Erreur base de données"

    try:
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

# Dashboard functions

def get_self_dashboard(session_token):
    """
    Récupère les informations du tableau de bord de l'utilisateur. Les informations dépendent du type de l'utilisateur.

    Args:
        session_token (str): Le jeton de session de l'utilisateur.

    Returns:
        Un tuple contenant les informations du tableau de bord (Dictionnaire python avec: Type utilisateur (candidat/participant), mail, username, Tags du candidat/participant, Nom et prénom pour candidat, Nom pour participant) et un message d'erreur si une erreur est survenue.
    """
    conn, cursor = get_db_connection()
    if conn is None:
        return None, "Erreur base de données"
    try:
        cursor.execute('''
        SELECT Candidate.id_candidate
        FROM Candidate
        JOIN "User" ON Candidate.id_user = "User".id_user
        WHERE "User".session_token = %s
        ''', (session_token,))
        candidate = cursor.fetchone()
        if candidate:
            cursor.execute('''
            SELECT Candidate.email_candidate, "User".username, Candidate.lastname_candidate, Candidate.name_candidate, Candidate.id_candidate, "User".id_user
            FROM Candidate
            JOIN "User" ON Candidate.id_user = "User".id_user
            WHERE Candidate.id_candidate = %s
            ''', (candidate['id_candidate'],))
            candidate_info = cursor.fetchone()
            cursor.execute('''
            SELECT Tag.id_tag, Tag.name_tag
            FROM Tag
            JOIN Candidate_tag ON Tag.id_tag = Candidate_tag.id_tag
            WHERE Candidate_tag.id_candidate = %s
            ''', (candidate['id_candidate'],))
            tags = cursor.fetchall()
            cursor.execute('''
            SELECT Event.*, COALESCE(json_agg(json_build_object(
                'id_interview', Interview.id_interview,
                'id_event', Interview.id_event,
                'id_candidate', Interview.id_candidate,
                'id_participant', Interview.id_participant,
                'start_time_interview', Interview.start_time_interview,
                'end_time_interview', Interview.end_time_interview,
                'feedback_candidate', Interview.feedback_candidate,
                'feedback_participant', Interview.feedback_participant,
                'happened', Interview.happened,
                'name_participant', Participant.name_participant,
                'lastname_candidate', Candidate.lastname_candidate,
                'name_candidate', Candidate.name_candidate
            )) FILTER (WHERE Interview.id_interview IS NOT NULL), '[]') AS interviews
            FROM Event
            LEFT JOIN Interview ON Event.id_event = Interview.id_event AND Interview.id_candidate = %s
            LEFT JOIN Participant ON Interview.id_participant = Participant.id_participant
            LEFT JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate
            GROUP BY Event.id_event
            ''', (candidate['id_candidate'],))
            events = cursor.fetchall()
            return {"type": "candidate", "mail": candidate_info['email_candidate'], "username": candidate_info['username'], "tags": tags, "lastname": candidate_info['lastname_candidate'], "name": candidate_info['name_candidate'], "events": events, "id_type": candidate_info['id_candidate'], "id_user": candidate_info['id_user']}, None


        cursor.execute('''
        SELECT Participant.id_participant
        FROM Participant
        JOIN "User" ON Participant.id_user = "User".id_user
        WHERE "User".session_token = %s
        ''', (session_token,))
        participant = cursor.fetchone()
        if participant:
            cursor.execute('''
            SELECT Participant.email_participant, "User".username, Participant.name_participant, Participant.id_participant, "User".id_user
            FROM Participant
            JOIN "User" ON Participant.id_user = "User".id_user
            WHERE Participant.id_participant = %s
            ''', (participant['id_participant'],))
            participant_info = cursor.fetchone()
            cursor.execute('''
            SELECT Tag.id_tag, Tag.name_tag
            FROM Tag
            JOIN Participant_tag ON Tag.id_tag = Participant_tag.id_tag
            WHERE Participant_tag.id_participant = %s
            ''', (participant['id_participant'],))
            tags = cursor.fetchall()
            cursor.execute('''
            SELECT Event.*, COALESCE(json_agg(json_build_object(
                'id_interview', Interview.id_interview,
                'id_event', Interview.id_event,
                'id_candidate', Interview.id_candidate,
                'id_participant', Interview.id_participant,
                'start_time_interview', Interview.start_time_interview,
                'end_time_interview', Interview.end_time_interview,
                'feedback_candidate', Interview.feedback_candidate,
                'feedback_participant', Interview.feedback_participant,
                'happened', Interview.happened,
                'name_participant', Participant.name_participant,
                'lastname_candidate', Candidate.lastname_candidate,
                'name_candidate', Candidate.name_candidate
            )) FILTER (WHERE Interview.id_interview IS NOT NULL), '[]') AS interviews
            FROM Event
            LEFT JOIN Interview ON Event.id_event = Interview.id_event AND Interview.id_participant = %s
            LEFT JOIN Participant ON Interview.id_participant = Participant.id_participant
            LEFT JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate
            GROUP BY Event.id_event
            ''', (participant['id_participant'],))
            events = cursor.fetchall()
            return {"type": "participant", "name":participant_info['name_participant'], "mail": participant_info['email_participant'], "username": participant_info['username'], "tags": tags, "events": events, "id_type": participant_info['id_participant'], "id_user": participant_info['id_user']}, None
        return None, "Utilisateur non trouvé"
    except psycopg2.Error as e:
        print(f"Erreur requête base de données: {e}")
        return None, "Erreur requête base de données"