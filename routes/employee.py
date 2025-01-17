from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database
import random, string

employee_bp = Blueprint('employee', __name__)

@employee_bp.route("/admin/employee")
def employee():
    return render_template('employee.html')

@employee_bp.route("/admin/manage_employee/employee/<int:id_employee>", methods=['GET', 'POST'])
def edit_employee(id_employee):
    employee, error = database.get_employee(id_employee)
    tags, error = database.get_all_tags()

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
            error = database.edit_employee(lastname, name, email, id_employee)
            if error is None:
                flash("Candidat mis à jour avec succès!", "success")
                return redirect(url_for('employee.edit_employee', id_employee=id_employee))
            else:
                flash(f"Erreur lors de la mise à jour du candidat: {error}", "danger")
                return redirect(url_for('employee.edit_employee', id_employee=id_employee))

    # Generate random password min 8 characters max 16 characters with at least one uppercase letter, one lowercase letter, one number and one special character
    password = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(random.randint(8, 16)))
    return render_template('employee.html', employee=employee, rpassword=password)

@employee_bp.route("/admin/manage_employee/employee/<int:id_employee>/delete", methods=['POST'])
def delete_employee(id_employee):
    database.delete_employee(id_employee)
    return redirect(url_for('manage_employee.manage_employee'))