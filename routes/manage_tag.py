from flask import Blueprint, render_template, redirect, url_for, flash
from lib import database

manage_tag_bp = Blueprint('manage_tag', __name__)

@manage_tag_bp.route("/admin/manage_tag")
def manage_tag():
    tags, error = database.get_all_tags()
    if error:
        flash("Erreur lors de la récupération des tags", "danger")
    return render_template('manage_tag.html', tags=tags)

@manage_tag_bp.route("/admin/manage_tag/<int:id_tag>/delete", methods=['POST'])
def delete_tag(id_tag):
    error = database.delete_tag(id_tag)
    if error:
        flash(f"Erreur lors de la suppression du tag: {error}", "danger")
    return redirect(url_for('manage_tag.manage_tag'))