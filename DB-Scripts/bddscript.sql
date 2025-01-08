CREATE TABLE Candidate(
   id_candidate INTEGER,
   lastname_candidate TEXT NOT NULL,
   name_candidate TEXT NOT NULL,
   email_candidate TEXT NOT NULL,
   PRIMARY KEY(id_candidate)
);

CREATE TABLE Participant(
   id_participant INTEGER,
   name_participant TEXT NOT NULL,
   email_participant TEXT,
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
   id_participant INTEGER NOT NULL,
   id_event INTEGER NOT NULL,
   id_candidate INTEGER NOT NULL,
   PRIMARY KEY(id_interview),
   FOREIGN KEY(id_participant) REFERENCES Participant(id_participant),
   FOREIGN KEY(id_event) REFERENCES Event(id_event),
   FOREIGN KEY(id_candidate) REFERENCES Candidate(id_candidate)
);

CREATE TABLE Participates(
   id_candidate INTEGER,
   id_event INTEGER,
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