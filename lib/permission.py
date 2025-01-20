from flask import flash, redirect, request, url_for
from lib import auth

checks = {
    '/admin': 'view_dashboards'
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