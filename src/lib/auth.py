from lib import database
import bcrypt, hashlib, random, requests, os
from sock import app

def verify_login(username, password):
    dbhashed_password, error = database.auth_get_hashedpassword(username)
    if error:
        return False, error
    if not dbhashed_password:
        return False, "Aucun utilisateur trouvé."
    dbhashed_password = dbhashed_password['password_user'].encode('utf-8')
    if bcrypt.checkpw(password.encode('utf-8'), dbhashed_password):
        session, error = database.auth_get_session(username)
        if error:
            return False, error
        return session, None
    else:
        return False, error

def genpassword(password):
    salt = bcrypt.gensalt(random.randint(12,16))
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    return hashed_password

def update_user_pass(password, user_id):
    session_token = hashlib.md5(random.randbytes(random.randint(8,32))).hexdigest()
    error = database.auth_update_password(genpassword(password), session_token, user_id)
    return error

def update_user(password, username):
    session_token = hashlib.md5(random.randbytes(random.randint(8,32))).hexdigest()
    error = database.update_user_password(username, genpassword(password), session_token)
    return error

def user_has_permission(user_id, permission_name):
    permissions, error = database.get_user_permissions(user_id)
    if error:
        return False
    return permission_name in permissions

def check_turnstile(response):
    secretkey = os.getenv('CF_SECRET')
    data = {
        "response": response,
        "secret": secretkey
    }
    r = requests.post("https://challenges.cloudflare.com/turnstile/v0/siteverify", data=data)
    if r.json()['success']:
        return True
    else:
        return False

def check_permission(session, permission_name):
    if database.auth_is_superuser(session):
        return True
    perms, error = database.auth_get_perms_from_session(session)
    app.logger.info(perms)
    for perm in perms:
        if perm == '*':
            return True
        if '.*' in perm:
            if permission_name.startswith(perm[:-1]):
                return True
    if error:
        return False
    if permission_name in perms:
        return True
    else:
        return False