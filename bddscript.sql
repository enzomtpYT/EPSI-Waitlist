CREATE TABLE Candidat(
   id_candidat INTEGER,
   nom_candidat TEXT NOT NULL,
   prenom_candidat TEXT NOT NULL,
   adresse_mail_candidat TEXT NOT NULL,
   PRIMARY KEY(id_candidat)
);

CREATE TABLE Intervenant(
   id_intervenant INTEGER,
   nom_intervenant TEXT NOT NULL,
   adresse_mail_intervenant TEXT,
   PRIMARY KEY(id_intervenant)
);

CREATE TABLE Evenement(
   id_evenement INTEGER,
   nom_evenement TEXT NOT NULL,
   date_evenement NUMERIC NOT NULL,
   PRIMARY KEY(id_evenement)
);

CREATE TABLE Entretien(
   id_entretien INTEGER,
   id_intervenant INTEGER NOT NULL,
   id_evenement INTEGER NOT NULL,
   id_candidat INTEGER NOT NULL,
   PRIMARY KEY(id_entretien),
   FOREIGN KEY(id_intervenant) REFERENCES Intervenant(id_intervenant),
   FOREIGN KEY(id_evenement) REFERENCES Evenement(id_evenement),
   FOREIGN KEY(id_candidat) REFERENCES Candidat(id_candidat)
);

CREATE TABLE Participe(
   id_candidat INTEGER,
   id_evenement INTEGER,
   PRIMARY KEY(id_candidat, id_evenement),
   FOREIGN KEY(id_candidat) REFERENCES Candidat(id_candidat),
   FOREIGN KEY(id_evenement) REFERENCES Evenement(id_evenement)
);

CREATE TABLE Assiste(
   id_intervenant INTEGER,
   id_evenement INTEGER,
   PRIMARY KEY(id_intervenant, id_evenement),
   FOREIGN KEY(id_intervenant) REFERENCES Intervenant(id_intervenant),
   FOREIGN KEY(id_evenement) REFERENCES Evenement(id_evenement)
);

INSERT INTO Candidat (id_candidat, nom_candidat, prenom_candidat, adresse_mail_candidat) VALUES
(1, 'Doe', 'John', 'john.doe@example.com'),
(2, 'Smith', 'Jane', 'jane.smith@example.com'),
(3, 'Brown', 'Charlie', 'charlie.brown@example.com');

INSERT INTO Intervenant (id_intervenant, nom_intervenant, adresse_mail_intervenant) VALUES
(1, 'Williams', 'williams@example.com'),
(2, 'Johnson', 'johnson@example.com');

INSERT INTO Evenement (id_evenement, nom_evenement, date_evenement) VALUES
(1, 'Tech Conference', '2023-11-01'),
(2, 'Job Fair', '2023-12-15');

INSERT INTO Entretien (id_entretien, id_intervenant, id_evenement, id_candidat) VALUES
(1, 1, 1, 1),
(2, 2, 2, 2);

INSERT INTO Participe (id_candidat, id_evenement) VALUES
(1, 1),
(2, 2),
(3, 1);

INSERT INTO Assiste (id_intervenant, id_evenement) VALUES
(1, 1),
(2, 2);