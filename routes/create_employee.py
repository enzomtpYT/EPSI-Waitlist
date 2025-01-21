from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from lib import database

create_employee_bp = Blueprint('create_employee', __name__)

@create_employee_bp.route('/admin/create_employee', methods=('GET', 'POST'))
def create_employee():
    if 'token' not in session:
        return redirect(url_for('auth.login'))
    session_token = session['token']
    user_role = database.get_user_role_with_token(session_token)
    if not user_role:
        flash('User role not found', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        lastname = request.form['employee_lastname']
        name = request.form['employee_name']
        email = request.form['employee_email']
        role = request.form['role']
        error = None

        if not lastname:
            error = 'Le nom de famille est obligatoire.'
        elif not name:
            error = 'Le prénom est obligatoire.'
        elif not email:
            error = 'L\'adresse email est obligatoire.'
        elif not role:
            error = 'Le rôle est obligatoire.'

        # Check if the user is allowed to assign the selected role
        if user_role == 'superadmin':
            allowed_roles = ['superadmin', 'admin', 'employee']
        elif user_role == 'admin':
            allowed_roles = ['admin', 'employee']
        elif user_role == 'employee':
            allowed_roles = ['employee']
        else:
            flash('Access denied', 'danger')
            return redirect(url_for('admin.create_employee'))

        if role not in allowed_roles:
            flash('You are not allowed to assign this role', 'danger')
            return redirect(url_for('admin.create_employee'))

        if error is None:
            error = database.create_employee(lastname, name, email, role)
            flash("Employé créé avec succès!", "success")
            return redirect(url_for('create_employee.create_employee'))
        else:
            flash(f"Erreur lors de la création de l'employé: {error}", "danger")

    return render_template('create_employee.html', user_role=user_role)