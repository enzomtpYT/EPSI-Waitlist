from flask import Blueprint, render_template, redirect, url_for, flash, request
from lib import database

manage_tag_bp = Blueprint('manage_tag', __name__)

@manage_tag_bp.route("/admin/manage_tag", methods=['GET', 'POST'])
def manage_tag():
    if request.method == 'POST':
        id_tag = request.form['id_tag']
        name = request.form['tag_name']
        error = None

        if not name:
            error = 'Le nom est obligatoire.'

        if error is None:
            error = database.edit_tag(name, id_tag)
            if error is None:
                flash("Tag mis à jour avec succès!", "success")
            else:
                flash(f"Erreur lors de la mise à jour du tag: {error}", "danger")
        else:
            flash(error, "danger")

    tags, error = database.get_all_tags()
    if error:
        flash("Erreur lors de la récupération des tags", "danger")
    return render_template('manage_tag.html', tags=tags)

# @manage_tag_bp.route("/admin/manage_tag")
# def manage_tag():
#     tags, error = database.get_all_tags()
#     if error:
#         flash("Erreur lors de la récupération des tags", "danger")
#     return render_template('manage_tag.html', tags=tags)

# @manage_tag_bp.route("/admin/manage_tag/<int:id_tag>/edit", methods=['GET', 'POST'])
# def edit_tag(id_tag):
#     tag, error = database.get_tag(id_tag)

#     if request.method == 'POST':
#         name = request.form['tag_name']
#         error = None

#         if not name:
#             error = 'Le nom est obligatoire.'

#         if error is None:
#             error = database.edit_tag(name, id_tag)
#             if error is None:
#                 flash("Tag mis à jour avec succès!", "success")
#                 return redirect(url_for('manage_tag.manage_tag'))
#             else:
#                 flash(f"Erreur lors de la mise à jour du tag: {error}", "danger")
#     return render_template('edit_tag.html', tag=tag)

@manage_tag_bp.route("/admin/manage_tag/<int:id_tag>/delete", methods=['POST'])
def delete_tag(id_tag):
    error = database.delete_tag(id_tag)
    if error:
        flash(f"Erreur lors de la suppression du tag: {error}", "danger")
    return redirect(url_for('manage_tag.manage_tag'))