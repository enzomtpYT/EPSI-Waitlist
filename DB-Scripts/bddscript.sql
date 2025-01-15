CREATE TABLE Candidate(
   id_candidate INTEGER,
   lastname_candidate TEXT NOT NULL,
   name_candidate TEXT NOT NULL,
   email_candidate TEXT NOT NULL,
   password_candidate TEXT NOT NULL,
   PRIMARY KEY(id_candidate)
);

CREATE TABLE Participant(
   id_participant INTEGER,
   name_participant TEXT NOT NULL,
   email_participant TEXT,
   password_participant TEXT NOT NULL,
   PRIMARY KEY(id_participant)
);

CREATE TABLE Event(
   id_event INTEGER,
   name_event TEXT NOT NULL,
   date_event NUMERIC NOT NULL,
   PRIMARY KEY(id_event)
);

CREATE TABLE Interview(
   id_interview INTEGER,
   happened NUMERIC NOT NULL DEFAULT 0,
   feedback_candidate TEXT,
   feedback_participant TEXT,
   duration_interview NUMERIC,
   id_participant INTEGER NOT NULL,
   id_event INTEGER NOT NULL,
   id_candidate INTEGER NOT NULL,
   PRIMARY KEY(id_interview),
   FOREIGN KEY(id_participant) REFERENCES Participant(id_participant),
   FOREIGN KEY(id_event) REFERENCES Event(id_event),
   FOREIGN KEY(id_candidate) REFERENCES Candidate(id_candidate),
   UNIQUE(id_candidate, id_participant, id_event) -- Add unique constraint to avoid duplicate interviews
);

CREATE TABLE Tag(
   id_tag INTEGER,
   name_tag TEXT NOT NULL,
   PRIMARY KEY(id_tag),
   UNIQUE(name_tag)
);

CREATE TABLE Office(
   id_employee INTEGER,
   lastname_employee TEXT NOT NULL,
   name_employee TEXT NOT NULL,
   email_employee TEXT NOT NULL,
   password_employee TEXT NOT NULL,
   PRIMARY KEY(id_employee)
);

CREATE TABLE Role(
   id_role INTEGER,
   name_role TEXT NOT NULL,
   PRIMARY KEY(id_role),
   UNIQUE(name_role)
);

CREATE TABLE Participates(
   id_candidate INTEGER,
   id_event INTEGER,
   weight INTEGER,
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

CREATE TABLE Employee_role(
   id_employee INTEGER,
   id_role INTEGER,
   PRIMARY KEY(id_employee, id_role),
   FOREIGN KEY(id_employee) REFERENCES Office(id_employee),
   FOREIGN KEY(id_role) REFERENCES Role(id_role)
);

CREATE TABLE Candidate_role(
   id_candidate INTEGER,
   id_role INTEGER,
   PRIMARY KEY(id_candidate, id_role),
   FOREIGN KEY(id_candidate) REFERENCES Candidate(id_candidate),
   FOREIGN KEY(id_role) REFERENCES Role(id_role)
);

CREATE TABLE Participant_role(
   id_participant INTEGER,
   id_role INTEGER,
   PRIMARY KEY(id_participant, id_role),
   FOREIGN KEY(id_participant) REFERENCES Participant(id_participant),
   FOREIGN KEY(id_role) REFERENCES Role(id_role)
);