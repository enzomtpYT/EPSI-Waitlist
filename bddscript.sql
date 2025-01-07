CREATE TABLE Candidate(
   id_candidate INTEGER,
   lastname_candidate TEXT NOT NULL,
   name_candidate TEXT NOT NULL,
   email_address_candidate TEXT NOT NULL,
   PRIMARY KEY(id_candidate)
);

CREATE TABLE Participant(
   id_Participant INTEGER,
   name_participant TEXT NOT NULL,
   email_address_participant TEXT,
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
   id_participant INTEGER NOT NULL,
   id_event INTEGER NOT NULL,
   id_candidate INTEGER NOT NULL,
   PRIMARY KEY(id_interview),
   FOREIGN KEY(id_participant) REFERENCES participant(id_participant),
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

INSERT INTO Candidate (id_candidate, lastname_candidate, name_candidate, email_address_candidate) VALUES
(1, 'Doe', 'John', 'john.doe@example.com'),
(2, 'Smith', 'Jane', 'jane.smith@example.com'),
(3, 'Brown', 'Charlie', 'charlie.brown@example.com');

INSERT INTO Participant (id_participant, name_participant, email_address_participant) VALUES
(1, 'Williams', 'williams@example.com'),
(2, 'Johnson', 'johnson@example.com');

INSERT INTO Event (id_event, name_event, date_event) VALUES
(1, 'Tech Conference', '2023-11-01'),
(2, 'Job Fair', '2023-12-15');

INSERT INTO Interview (id_interview, id_participant, id_event, id_candidate) VALUES
(1, 1, 1, 1),
(2, 2, 2, 2);

INSERT INTO Participates (id_candidate, id_event) VALUES
(1, 1),
(2, 2),
(3, 1);

INSERT INTO Attends (id_participant, id_event) VALUES
(1, 1),
(2, 2);