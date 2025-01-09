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

CREATE TABLE Tag(
   id_tag INTEGER,
   name_tag TEXT NOT NULL,
   PRIMARY KEY(id_tag),
   UNIQUE(name_tag)
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

CREATE TABLE Member_of(
   id_candidate INTEGER,
   id_tag INTEGER,
   PRIMARY KEY(id_candidate, id_tag),
   FOREIGN KEY(id_candidate) REFERENCES Candidate(id_candidate),
   FOREIGN KEY(id_tag) REFERENCES Tag(id_tag)
);

CREATE TABLE Dedicated_to(
   id_event INTEGER,
   id_tag INTEGER,
   PRIMARY KEY(id_event, id_tag),
   FOREIGN KEY(id_event) REFERENCES Event(id_event),
   FOREIGN KEY(id_tag) REFERENCES Tag(id_tag)
);