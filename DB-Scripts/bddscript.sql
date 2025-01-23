CREATE TABLE Event(
   id_event INTEGER,
   name_event VARCHAR(50)  NOT NULL,
   date_event DATE NOT NULL,
   start_time_event TIME,
   end_time_event TIME,
   has_timeslots BOOLEAN NOT NULL,
   PRIMARY KEY(id_event)
);

CREATE TABLE Tag(
   id_tag INTEGER,
   name_tag VARCHAR(50)  NOT NULL,
   PRIMARY KEY(id_tag),
   UNIQUE(name_tag)
);

CREATE TABLE Role(
   id_role INTEGER,
   name_role VARCHAR(50)  NOT NULL,
   PRIMARY KEY(id_role),
   UNIQUE(name_role)
);

CREATE TABLE "User"(
   id_user INTEGER,
   username VARCHAR(50)  NOT NULL,
   password_user VARCHAR(100) ,
   session_token VARCHAR(100) ,
   PRIMARY KEY(id_user),
   UNIQUE(username)
);

CREATE TABLE Permission(
   id_permission INTEGER,
   name_permission VARCHAR(50)  NOT NULL,
   PRIMARY KEY(id_permission),
   UNIQUE(name_permission)
);

CREATE TABLE Timeslot(
   id_timeslot INTEGER,
   start_timeslot TIME NOT NULL,
   end_timeslot TIME NOT NULL,
   id_event INTEGER NOT NULL,
   PRIMARY KEY(id_timeslot),
   FOREIGN KEY(id_event) REFERENCES Event(id_event)
);

CREATE TABLE Candidate(
   id_candidate INTEGER,
   lastname_candidate VARCHAR(50)  NOT NULL,
   name_candidate VARCHAR(50)  NOT NULL,
   email_candidate VARCHAR(50)  NOT NULL,
   id_user INTEGER NOT NULL,
   PRIMARY KEY(id_candidate),
   UNIQUE(id_user),
   FOREIGN KEY(id_user) REFERENCES "User"(id_user)
);

CREATE TABLE Participant(
   id_participant INTEGER,
   name_participant VARCHAR(50)  NOT NULL,
   email_participant VARCHAR(50) ,
   location_participant VARCHAR(50) ,
   id_user INTEGER NOT NULL,
   PRIMARY KEY(id_participant),
   UNIQUE(id_user),
   FOREIGN KEY(id_user) REFERENCES "User"(id_user)
);

CREATE TABLE Interview(
   id_interview INTEGER,
   happened BOOLEAN NOT NULL,
   feedback_candidate VARCHAR(1000) ,
   feedback_participant VARCHAR(50) ,
   duration_interview TIME,
   id_participant INTEGER NOT NULL,
   id_event INTEGER NOT NULL,
   id_candidate INTEGER NOT NULL,
   PRIMARY KEY(id_interview),
   FOREIGN KEY(id_participant) REFERENCES Participant(id_participant),
   FOREIGN KEY(id_event) REFERENCES Event(id_event),
   FOREIGN KEY(id_candidate) REFERENCES Candidate(id_candidate)
);

CREATE TABLE Employee(
   id_employee INTEGER,
   lastname_employee VARCHAR(50)  NOT NULL,
   name_employee VARCHAR(50)  NOT NULL,
   email_employee VARCHAR(50)  NOT NULL,
   id_user INTEGER NOT NULL,
   PRIMARY KEY(id_employee),
   UNIQUE(id_user),
   FOREIGN KEY(id_user) REFERENCES "User"(id_user)
);

CREATE TABLE Attends(
   id_candidate INTEGER,
   id_event INTEGER,
   priority INTEGER,
   PRIMARY KEY(id_candidate, id_event),
   FOREIGN KEY(id_candidate) REFERENCES Candidate(id_candidate),
   FOREIGN KEY(id_event) REFERENCES Event(id_event)
);

CREATE TABLE Participates(
   id_participant INTEGER,
   id_event INTEGER,
   start_date_offer DATE,
   end_date_offer DATE,
   job_description_participant VARCHAR(50) ,
   nbr_position_participant INTEGER,
   pdf_job_offer VARCHAR(50) ,
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
   FOREIGN KEY(id_user) REFERENCES "User"(id_user)
);

CREATE TABLE Role_permission(
   id_role INTEGER,
   id_permission INTEGER,
   PRIMARY KEY(id_role, id_permission),
   FOREIGN KEY(id_role) REFERENCES Role(id_role),
   FOREIGN KEY(id_permission) REFERENCES Permission(id_permission)
);

CREATE TABLE Organizes(
   id_event INTEGER,
   id_employee INTEGER,
   PRIMARY KEY(id_event, id_employee),
   FOREIGN KEY(id_event) REFERENCES Event(id_event),
   FOREIGN KEY(id_employee) REFERENCES Employee(id_employee)
);

CREATE TABLE Timeslot_candidate(
   id_candidate INTEGER,
   id_timeslot INTEGER,
   PRIMARY KEY(id_candidate, id_timeslot),
   FOREIGN KEY(id_candidate) REFERENCES Candidate(id_candidate),
   FOREIGN KEY(id_timeslot) REFERENCES Timeslot(id_timeslot)
);

CREATE TABLE Timeslot_participant(
   id_participant INTEGER,
   id_timeslot INTEGER,
   PRIMARY KEY(id_participant, id_timeslot),
   FOREIGN KEY(id_participant) REFERENCES Participant(id_participant),
   FOREIGN KEY(id_timeslot) REFERENCES Timeslot(id_timeslot)
);

CREATE TABLE Timeslot_employee(
   id_employee INTEGER,
   id_timeslot INTEGER,
   PRIMARY KEY(id_employee, id_timeslot),
   FOREIGN KEY(id_employee) REFERENCES Employee(id_employee),
   FOREIGN KEY(id_timeslot) REFERENCES Timeslot(id_timeslot)
);
