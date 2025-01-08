from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from lib.database import get_db_connection

create_participant_bp = Blueprint('create_participant', __name__)

@create_participant_bp.route('/admin/create_participant', methods=('GET', 'POST'))
def create_participant():
    return render_template('create_participant.html')