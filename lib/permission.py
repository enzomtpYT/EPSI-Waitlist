from flask import flash, redirect, request, url_for
from lib import auth

checks = {
    '/admin': 'admin.access',
    '/admin/manage_candidate': 'admin.dashboard.view.candidate',
    '/admin/manage_participant': 'admin.dashboard.view.participant',
    '/admin/manage_event': 'admin.dashboard.view.events',
    '/admin/manage_tag': 'admin.dashboard.view.tags',
    '/admin/manage_employee': 'admin.dashboard.view.office',
    '/admin/create_candidate': 'admin.dashboard.create.candidate',
    '/admin/create_participant': 'admin.dashboard.create.participant',
    '/admin/create_event': 'admin.dashboard.create.event',
    '/admin/create_tag': 'admin.dashboard.create.tag',
    '/admin/create_employee': 'admin.dashboard.create.office',
    '/admin/manage_candidate/candidate': 'admin.dashboard.create.candidate',
    '/admin/manage_participant/participant': 'admin.dashboard.create.participant',
    '/admin/manage_event/event': 'admin.dashboard.create.event',
    '/admin/manage_employee/employee': 'admin.dashboard.create.office',
    '/participant/dashboard': 'participant.dashboard',
    '/candidate/dashboard': 'candidate.dashboard',
    '/interviews': 'interviews.view',

}

def checkroutes(session):
    for route, perm in checks.items():
        if request.path.startswith(route):
            print(f'Checking if user has permission {perm} for route {route}')
            if 'token' not in session:
                print('No token in session')
                return redirect(url_for('auth.login'))
            if not auth.check_permission(session['token'], perm):
                flash("You don't have permission to access this page.")
                return redirect('/')
            print('User has permission')