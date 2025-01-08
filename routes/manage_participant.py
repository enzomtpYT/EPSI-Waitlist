from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from lib.database import get_db_connection

manage_participant_bp = Blueprint('manage_participant', __name__)

@manage_participant_bp.route('/admin/manage_participant', methods=('GET', 'POST'))
def manage_participant():
    return render_template('manage_participant.html')