from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from lib import database, auth

employee_bp = Blueprint('employee', __name__)

@employee_bp.route("/admin/employee")
def employee():
    return render_template('employee.html')

@employee_bp.route("/admin/manage_employee/employee/<int:id_employee>", methods=['GET', 'POST'])
def edit_employee(id_employee):
    if 'token' not in session:
        return redirect(url_for('auth.login'))
    session_token = session['token']
    user_role = database.get_user_role_with_token(session_token)
    if not user_role:
        flash('User role not found', 'danger')
        return redirect(url_for('auth.login'))

    employee, error = database.get_employee(id_employee)
    employee_role, error = database.get_user_role(employee['id_user'])
    if error:
        flash(error, 'danger')
        return redirect(url_for('employee.employee'))

    if request.method == 'POST':
        lastname = request.form['employee_lastname']
        name = request.form['employee_name']
        email = request.form['employee_email']
        password = request.form['password']
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

        # Check if the current user is allowed to assign the selected role
        allowed_roles = []
        if user_role == 'superadmin':
            allowed_roles = ['superadmin', 'admin', 'employee']
        elif user_role == 'admin':
            allowed_roles = ['admin', 'employee']
        elif user_role == 'employee':
            allowed_roles = ['employee']

        if role not in allowed_roles:
            flash('You are not allowed to assign this role', 'danger')
            return redirect(url_for('employee.edit_employee', id_employee=id_employee))

        if error is None:
            # Update the employee in the database
            if password:
                error = auth.update_user(password, email)
            error = database.edit_employee(lastname, name, email, id_employee)
            if error is None:
                # Update the employee's role
                error = database.update_user_role(employee['id_user'], role)
                if error is None:
                    flash("Employé.e mis à jour avec succès!", "success")
                    return redirect(url_for('employee.edit_employee', id_employee=id_employee))
                else:
                    flash(f"Erreur lors de la mise à jour du Employé.e: {error}", "danger")
                    return redirect(url_for('employee.edit_employee', id_employee=id_employee))

    return render_template('employee.html', employee=employee, employee_role=employee_role, user_role=user_role)

@employee_bp.route("/admin/manage_employee/employee/<int:id_employee>/delete", methods=['POST'])
def delete_employee(id_employee):
    error = database.delete_employee(id_employee)
    if error:
        flash(f"Erreur lors de la suppression de l'employé.e: {error}", "danger")
        return redirect(url_for('employee.edit_employee', id_employee=id_employee))
    flash("Employé.e supprimé.e avec succès!", "success")
    return redirect(url_for('manage_employee.manage_employee'))