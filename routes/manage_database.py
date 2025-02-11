from flask import Blueprint, render_template, redirect, url_for, flash, request
import csv
import io
from lib import database

manage_database_bp = Blueprint('manage_database', __name__)

@manage_database_bp.route("/admin/manage_database")
def manage_database():
    return render_template('manage_database.html')

@manage_database_bp.route("/admin/manage_database/import_csv", methods=['GET', 'POST'])
def import_csv():
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('Aucun fichier sélectionné', 'danger')
            return redirect(url_for('manage_database.manage_database'))

        file = request.files['csv_file']
        if file.filename == '':
            flash('Aucun fichier sélectionné', 'danger')
            return redirect(url_for('manage_database.manage_database'))

        if file and file.filename.endswith('.csv'):
            try:
                stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                csv_input = csv.reader(stream)
                headers = next(csv_input)  # Skip the header row
                for row in csv_input:
                    # Process each row and update the database
                    error = database.update_from_csv_row(row)
                    if error:
                        flash(f"Erreur lors de la mise à jour de la base de données: {error}", "danger")
                        return redirect(url_for('manage_database.manage_database'))
                flash('Base de données mise à jour avec succès!', 'success')
                return redirect(url_for('manage_database.import_csv'))
            except Exception as e:
                flash(f"Erreur lors du traitement du fichier CSV: {e}", 'danger')
                return redirect(url_for('manage_database.manage_database'))
        else:
            flash('Format de fichier non valide. Veuillez télécharger un fichier CSV.', 'danger')
            return redirect(url_for('manage_database.manage_database'))

    return render_template('manage_database.html')