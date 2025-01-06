from flask import Blueprint, render_template, g
import sqlite3, datetime

liste_bp = Blueprint('liste', __name__)

def get_db_connection():
    try:
        conn = sqlite3.connect('BDDStage')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

today = datetime.date.today()

def get_event():
    conn = get_db_connection()
    if conn is None:
        return None, "Database connection error"
    try:
        events = conn.execute(f'SELECT id_evenement FROM Evenement WHERE date_evenement = \'{today}\'').fetchall()
        return events[0]['id_evenement'], None
    except sqlite3.Error as e:
        print(f"Database query error: {e}")
        return None, "Database query error"
    finally:
        conn.close()

def get_candidats(todayevent):
    conn = get_db_connection()
    if conn is None:
        return None, "Database connection error"
    try:
        candids = conn.execute(f'SELECT id_candidat FROM Participe WHERE id_evenement = \'{todayevent}\'').fetchall()
        candid = []
        for candidat in candids:
            candid.append(conn.execute(f'SELECT * FROM Candidat WHERE id_candidat = \'{candidat["id_candidat"]}\'').fetchall()[0])
    except sqlite3.Error as e:
        print(f"Database query error: {e}")
        return None, "Database query error"
    finally:
        conn.close()
    return candid, None

def get_intervenant(todayevent):
    conn = get_db_connection()
    if conn is None:
        return None, "Database connection error"
    try:
        inters = conn.execute(f'SELECT id_intervenant FROM Assiste WHERE id_evenement = \'{todayevent}\'').fetchall()
        inter = []
        for intervenant in inters:
            inter.append(conn.execute(f'SELECT * FROM Intervenant WHERE id_intervenant = \'{intervenant["id_intervenant"]}\'').fetchall()[0])
    except sqlite3.Error as e:
        print(f"Database query error: {e}")
        return None, "Database query error"
    finally:
        conn.close()
    return inter, None

@liste_bp.route("/liste")
def liste():
    todayevent, error = get_event()
    if error:
        return error, 500
    if not todayevent:
        return "No events found", 404
    candid, error = get_candidats(todayevent)
    if error:
        return error, 500
    if not candid:
        return "No candidates found", 404
    inter, error = get_intervenant(todayevent)
    if error:
        return error, 500
    if not inter:
        return "No intervenants found", 404

    return render_template('liste.html', candidats=candid, intervenants=inter)
