from lib import database
import bcrypt, hashlib, random, requests

def verify_login(username, password):
    dbhashed_password, error = database.auth_get_hashedpassword(username)
    dbhashed_password = dbhashed_password[0]
    if error:
        return False, error
    if bcrypt.checkpw(password.encode('utf-8'), dbhashed_password):
        session, error = database.auth_get_session(username)
        if error:
            return False, error
        return session, None
    else:
        return False, error

def genpassword(password):
    salt = bcrypt.gensalt(random.randint(12,16))
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def register_candidate(id_candidate, password):
    username = database.get_candidate_email(id_candidate)
    session_token = hashlib.md5(random.randbytes(random.randint(8,32))).hexdigest()
    error = database.auth_register_candidate(id_candidate, username, genpassword(password), session_token)
    return error

def register_participant(id_participant, password):
    username = database.get_participant_email(id_participant)
    session_token = hashlib.md5(random.randbytes(random.randint(8,32))).hexdigest()
    error = database.auth_register_participant(id_participant, username, genpassword(password), session_token)
    return error

def register_employee(id_employee, password):
    username = database.get_employee_email(id_employee)
    session_token = hashlib.md5(random.randbytes(random.randint(8,32))).hexdigest()
    error = database.auth_register_employee(id_employee, username, genpassword(password), session_token)
    return error

def user_has_permission(user_id, permission_name):
    permissions, error = database.get_user_permissions(user_id)
    if error:
        return False
    return permission_name in permissions

def check_turnstile(response):
    secretkey = "0x4AAAAAAA5lAF_NTbcBlcVnVcwfmmhB4VE"
    data = {
        "response": response,
        "secret": secretkey
    }
    r = requests.post("https://challenges.cloudflare.com/turnstile/v0/siteverify", data=data)
    if r.json()['success']:
        return True
    else:
        return False