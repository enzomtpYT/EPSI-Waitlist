CREATE TABLE Event(
   id_event INTEGER,
   name_event TEXT NOT NULL,
   date_event NUMERIC NOT NULL,
   PRIMARY KEY(id_event)
);

CREATE TABLE Tag(
   id_tag INTEGER,
   name_tag TEXT NOT NULL,
   PRIMARY KEY(id_tag),
   UNIQUE(name_tag)
);

CREATE TABLE Role(
   id_role INTEGER,
   name_role TEXT NOT NULL,
   PRIMARY KEY(id_role),
   UNIQUE(name_role)
);

CREATE TABLE User(
   id_user INTEGER,
   username TEXT NOT NULL,
   password_user TEXT,
   salt TEXT,
   session_token TEXT,
   PRIMARY KEY(id_user),
   UNIQUE(username),
   UNIQUE(session_token)
);

CREATE TABLE Permission(
   id_permission INTEGER,
   name_permission TEXT NOT NULL,
   PRIMARY KEY(id_permission),
   UNIQUE(name_permission)
);

CREATE TABLE Candidate(
   id_candidate INTEGER,
   lastname_candidate TEXT NOT NULL,
   name_candidate TEXT NOT NULL,
   email_candidate TEXT NOT NULL,
   id_user INTEGER,
   PRIMARY KEY(id_candidate),
   FOREIGN KEY(id_user) REFERENCES User(id_user) ON DELETE CASCADE
);

CREATE TABLE Participant(
   id_participant INTEGER,
   name_participant TEXT NOT NULL,
   email_participant TEXT,
   id_user INTEGER,
   PRIMARY KEY(id_participant),
   FOREIGN KEY(id_user) REFERENCES User(id_user) ON DELETE CASCADE
);

CREATE TABLE Interview(
   id_interview INTEGER,
   happened NUMERIC NOT NULL,
   feedback_candidate TEXT,
   feedback_participant TEXT,
   duration_interview NUMERIC,
   id_participant INTEGER NOT NULL,
   id_event INTEGER NOT NULL,
   id_candidate INTEGER NOT NULL,
   PRIMARY KEY(id_interview),
   FOREIGN KEY(id_participant) REFERENCES Participant(id_participant),
   FOREIGN KEY(id_event) REFERENCES Event(id_event),
   FOREIGN KEY(id_candidate) REFERENCES Candidate(id_candidate)
);

CREATE TABLE Office(
   id_employee INTEGER,
   lastname_employee TEXT NOT NULL,
   name_employee TEXT NOT NULL,
   email_employee TEXT NOT NULL,
   id_user INTEGER,
   PRIMARY KEY(id_employee),
   FOREIGN KEY(id_user) REFERENCES User(id_user) ON DELETE CASCADE
);

CREATE TABLE Participates(
   id_candidate INTEGER,
   id_event INTEGER,
   priority INTEGER,
   PRIMARY KEY(id_candidate, id_event),
   FOREIGN KEY(id_candidate) REFERENCES Candidate(id_candidate),
   FOREIGN KEY(id_event) REFERENCES Event(id_event)
);

CREATE TABLE Attends(
   id_participant INTEGER,
   id_event INTEGER,
   PRIMARY KEY(id_participant, id_event),
   FOREIGN KEY(id_participant) REFERENCES Participant(id_participant),
   FOREIGN KEY(id_event) REFERENCES Event(id_event)
);

CREATE TABLE Candidate_tag(
   id_candidate INTEGER,
   id_tag INTEGER,
   PRIMARY KEY(id_candidate, id_tag),
   FOREIGN KEY(id_candidate) REFERENCES Candidate(id_candidate),
   FOREIGN KEY(id_tag) REFERENCES Tag(id_tag)
);

CREATE TABLE Event_tag(
   id_event INTEGER,
   id_tag INTEGER,
   PRIMARY KEY(id_event, id_tag),
   FOREIGN KEY(id_event) REFERENCES Event(id_event),
   FOREIGN KEY(id_tag) REFERENCES Tag(id_tag)
);

CREATE TABLE Participant_tag(
   id_participant INTEGER,
   id_tag INTEGER,
   PRIMARY KEY(id_participant, id_tag),
   FOREIGN KEY(id_participant) REFERENCES Participant(id_participant),
   FOREIGN KEY(id_tag) REFERENCES Tag(id_tag)
);

CREATE TABLE User_role(
   id_role INTEGER,
   id_user INTEGER,
   PRIMARY KEY(id_role, id_user),
   FOREIGN KEY(id_role) REFERENCES Role(id_role),
   FOREIGN KEY(id_user) REFERENCES User(id_user) ON DELETE CASCADE
);

CREATE TABLE Role_permission(
   id_role INTEGER,
   id_permission INTEGER,
   PRIMARY KEY(id_role, id_permission),
   FOREIGN KEY(id_role) REFERENCES Role(id_role),
   FOREIGN KEY(id_permission) REFERENCES Permission(id_permission)
);
