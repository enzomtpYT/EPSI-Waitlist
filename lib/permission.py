from flask import flash, redirect, request, url_for
from lib import auth

checks = {
    '/admin': 'admin.acess',
    '/admin/manage_candidate': 'dashboard.view.candidate',
    '/admin/manage_participant': 'dashboard.view.participant',
    '/admin/manage_event': 'dashboard.view.events',
    '/admin/manage_tag': 'dashboard.view.tags',
    '/admin/manage_employee': 'dashboard.view.office',
    '/admin/create_candidate': 'dashboard.create.candidate',
    '/admin/create_participant': 'dashboard.create.participant',
    '/admin/create_event': 'dashboard.create.event',
    '/admin/create_tag': 'dashboard.create.tag',
    '/admin/create_employee': 'dashboard.create.office',
    '/admin/manage_candidate/candidate': 'dashboard.create.candidate',
    '/admin/manage_participant/participant': 'dashboard.create.participant',
    '/admin/manage_event/event': 'dashboard.create.event',
    '/admin/manage_employee/employee': 'dashboard.create.office'
    
}

def checkroutes(session):
    for route, perm in checks.items():
        if request.path.startswith(route):
            print(f'Checking if user has permission {perm} for route {route}')
            if 'token' not in session:
                return redirect(url_for('auth.login'))
            if not auth.check_permission(session['token'], perm):
                flash("You don't have permission to access this page.")
                return redirect('/')