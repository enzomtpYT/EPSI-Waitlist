from flask import Blueprint, render_template, redirect, url_for, flash
from lib import database

manage_employee_bp = Blueprint('manage_employee', __name__)

@manage_employee_bp.route("/admin/manage_employee")
def manage_employee():
    return render_template('manage_employee.html')