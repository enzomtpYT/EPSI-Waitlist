from flask import flash, jsonify, redirect, request, url_for
from lib import auth

checks = {
    '/admin': 'admin.access',
    '/admin/manage_candidate': 'admin.dashboard.view.candidate',
    '/admin/manage_participant': 'admin.dashboard.view.participant',
    '/admin/manage_event': 'admin.dashboard.view.events',
    '/admin/manage_tag': 'admin.dashboard.view.tags',
    '/admin/manage_employee': 'admin.dashboard.view.employee',

    '/api/add/candidate': 'admin.dashboard.create.candidate',
    '/api/add/participant': 'admin.dashboard.create.participant',
    '/api/add/event': 'admin.dashboard.create.event',
    '/api/add/tag': 'admin.dashboard.create.tag',
    '/api/add/employee': 'admin.dashboard.create.employee',

    '/api/update/candidate': 'admin.dashboard.update.candidate',
    '/api/update/participant': 'admin.dashboard.update.participant',
    '/api/update/event': 'admin.dashboard.update.event',
    '/api/update/tag': 'admin.dashboard.update.tag',
    '/api/update/employee': 'admin.dashboard.update.employee',

    '/api/delete/candidate': 'admin.dashboard.delete.candidate',
    '/api/delete/participant': 'admin.dashboard.delete.participant',
    '/api/delete/event': 'admin.dashboard.delete.event',
    '/api/delete/tag': 'admin.dashboard.delete.tag',
    '/api/delete/employee': 'admin.dashboard.delete.employee',

    '/participant/dashboard': 'participant.dashboard',
    '/candidate/dashboard': 'candidate.dashboard',
    '/interviews': 'interviews.view',

    '/api/archive_schema': 'admin.database.archive',
    '/api/wipe_candidate': 'admin.database.delete',
    '/admin/manage_database': 'admin.database.view',
}

def checkroutes(session):
    for route, perm in checks.items():
        if route.startswith('/api') and request.path.startswith(route):
            print(f'Checking if user has permission {perm} for route {route}')
            if 'token' not in session:
                print('No token in session')
                return jsonify({"error": "Token manquant"}), 400
            if not auth.check_permission(session['token'], perm):
                print('User does not have permission')
                return jsonify({"error": "Permission manquantes."}), 403
            print('User has permission')
        
        elif request.path.startswith(route):
            print(f'Checking if user has permission {perm} for route {route}')
            if 'token' not in session:
                print('No token in session')
                return redirect(url_for('auth.login'))
            if not auth.check_permission(session['token'], perm):
                flash("Permission manquantes pour accèder à cet page.", "danger")
                return redirect('/')
            print('User has permission')