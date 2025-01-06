from flask import Blueprint, render_template, g
import sqlite3

liste_bp = Blueprint('liste', __name__)

def get_db_connection():
    try:
        conn = sqlite3.connect('BDDStage')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

@liste_bp.route("/liste")
def liste():
    conn = get_db_connection()
    if conn is None:
        return "Database connection error", 500
    try:
        items = conn.execute('SELECT * FROM Candidat').fetchall()
    except sqlite3.Error as e:
        print(f"Database query error: {e}")
        return f"Database query error", 500
    finally:
        conn.close()
    return render_template('liste.html', cand=items)
