from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database

create_employee_bp = Blueprint('create_employee', __name__)

@create_employee_bp.route('/admin/create_employee', methods=('GET', 'POST'))
def create_employee():
    if request.method == 'POST':
        lastname = request.form['employee_lastname']
        name = request.form['employee_name']
        email = request.form['employee_email']
        error = None

        if not lastname:
            error = 'Le nom de famille est obligatoire.'
        elif not name:
            error = 'Le prénom est obligatoire.'
        elif not email:
            error = 'L\'adresse email est obligatoire.'

        if error is None:
            employee_id, error = database.create_employee(lastname, name, email)
            flash("Employé créé avec succès!", "success")
            return redirect(url_for('create_employee.create_employee'))
        else:
            flash(f"Erreur lors de la création de l'employé: {error}", "danger")

    return render_template('create_employee.html')