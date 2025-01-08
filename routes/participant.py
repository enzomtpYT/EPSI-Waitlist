from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from lib.database import get_db_connection

participant_bp = Blueprint('participant', __name__)

@participant_bp.route('/admin/participant', methods=('GET', 'POST'))
def participant():
    return render_template('participant.html')