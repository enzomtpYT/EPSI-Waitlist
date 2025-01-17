from lib import database
import bcrypt, datetime, hashlib

def verify_login(username, password):
    salt, error = database.auth_get_salt(username)
    if error:
        return False, error
    dbhashed_password, error = database.auth_get_hashedpassword(username)
    dbhashed_password = dbhashed_password[0]
    if error:
        return False, error
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt[0])
    if hashed_password == dbhashed_password:
        session, error = database.auth_get_session(username)
        if error:
            return False, error
        return session, None
    else:
        return False, error

def register_candidate(id_candidate, password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    username = database.get_candidate_email(id_candidate)
    session_token = hashlib.md5((datetime.datetime.now().strftime('%Y%m%d%H%M%S') + username).encode('utf-8')).hexdigest()
    error = database.auth_register_candidate(id_candidate, username, hashed_password, salt, session_token)
    return error

def register_participant(id_participant, password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    username = database.get_participant_email(id_participant)
    session_token = hashlib.md5((datetime.datetime.now().strftime('%Y%m%d%H%M%S') + username).encode('utf-8')).hexdigest()
    error = database.auth_register_participant(id_participant, username, hashed_password, salt, session_token)
    return error

def register_employee(id_employee, password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    username = database.get_employee_email(id_employee)
    session_token = hashlib.md5((datetime.datetime.now().strftime('%Y%m%d%H%M%S') + username).encode('utf-8')).hexdigest()
    error = database.auth_register_employee(id_employee, username, hashed_password, salt, session_token)
    return error