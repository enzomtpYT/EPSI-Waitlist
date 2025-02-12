from flask import Blueprint, render_template, redirect, url_for, flash
from lib import database

manage_employee_bp = Blueprint('manage_employee', __name__)

@manage_employee_bp.route("/admin/manage_employee")
def manage_employee():
    employees, error = database.get_all_employees()
    if error:
        flash("Erreur lors de la récupération des employés", "danger")
        return render_template('manage_employee.html', employees=[])
    return render_template('manage_employee.html', employees=employees)

@manage_employee_bp.route("/admin/manage_employee/<int:id_employee>/delete", methods=['POST'])
def delete_employee(id_employee):
    error = database.delete_employee(id_employee)
    if error:
        flash(f"Erreur lors de la suppression de l'employé: {error}", "danger")
    return redirect(url_for('manage_employee.manage_employee'))