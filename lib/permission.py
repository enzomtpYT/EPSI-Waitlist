from flask import redirect, request, url_for
from lib import auth

def checkroutes(session):
    
    if request.path.startswith('/admin'):
        if auth.check_permission(session['token'], 'view_dashboards'):
            print(f'Admin route accessed with session: {session['token']}')
        else:
            return redirect(url_for('auth.login'))