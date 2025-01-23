INSERT INTO public."User" (id_user,username,password_user,session_token) VALUES
	 (2,'laval@email.fr','$2b$12$19nrk22vpp0sD7T39nOkE.16/OtJQpEGJ3Dvad/WM5/Yqd7xE3LKS','ccc48c36fb8fbcc21ed3951ab2afcb1f'),
	 (3,'hebdo@email.fr',NULL,NULL),
	 (4,'lailis@email.fr',NULL,NULL),
	 (5,'sep@email.fr','$2b$14$GCWVsMn/324u0rgv4ul1oeijfnKYJ/PNkM1wrB/6zjzgaF7Nl5yMG','90629bc4fe048455301f678d6c9d55a4'),
	 (6,'alibox@mail.fr','$2b$13$VOOd0S5WX.XBwJVOSchm8.pS1WOXwX8OF7nQKIdcbiRHjYrE03wVi','513b17974641a3f3db521c344e17916a'),
	 (7,'marinedup@email.fr','$2b$13$8h/k0U9jzQInSovKM4E8WOXYMlHYG/aqrsdQJZ2BnmySvmIfnCL3i','d9bfc7783f5035d21e063f11dc340193'),
	 (1,'superuser@mail.fr','$2y$10$3Lhk/.DzcxiMDHqPkshyhObEsBixnUrXXkL367jVoZEQ3UBz7ZG8W','ce3903a8cc204d85856b06b89264bbbe');
INSERT INTO public.attends (id_candidate,id_event,priority) VALUES
	 (1,1,1),
	 (2,1,8),
	 (1,2,1),
	 (2,2,9),
	 (3,2,1);
INSERT INTO public.candidate (id_candidate,lastname_candidate,name_candidate,email_candidate,id_user) VALUES
	 (1,'Laval','Bernard','laval@email.fr',2),
	 (2,'Hebdo','Charlie','hebdo@email.fr',3),
	 (3,'Doeya','Lailis','lailis@email.fr',4);
INSERT INTO public.candidate_tag (id_candidate,id_tag) VALUES
	 (1,1),
	 (2,1),
	 (3,4);
INSERT INTO public.employee (id_employee,lastname_employee,name_employee,email_employee,id_user) VALUES
	 (1,'User','Super','superuser@mail.fr',1),
	 (2,'Dupont','Marine','marinedup@email.fr',7);
INSERT INTO public."event" (id_event,name_event,date_event,start_time_event,end_time_event,has_timeslots) VALUES
	 (1,'Forum Stage','2025-01-23',NULL,NULL,false),
	 (2,'Forum S1','2025-01-31',NULL,NULL,false);
INSERT INTO public.event_tag (id_event,id_tag) VALUES
	 (1,1),
	 (1,2),
	 (1,3),
	 (2,4),
	 (2,5),
	 (2,6);
INSERT INTO public.interview (id_interview,happened,feedback_candidate,feedback_participant,duration_interview,id_participant,id_event,id_candidate) VALUES
	 (1,false,NULL,NULL,NULL,1,2,1),
	 (2,false,NULL,NULL,NULL,2,2,2),
	 (3,false,NULL,NULL,NULL,2,2,3);
INSERT INTO public.participant (id_participant,name_participant,email_participant,location_participant,id_user) VALUES
	 (1,'Septeo','sep@email.fr',NULL,5),
	 (2,'Alibox','alibox@mail.fr',NULL,6);
INSERT INTO public.participant_tag (id_participant,id_tag) VALUES
	 (1,7),
	 (2,7);
INSERT INTO public.participates (id_participant,id_event,start_date_offer,end_date_offer,job_description_participant,nbr_position_participant,pdf_job_offer) VALUES
	 (1,1,NULL,NULL,NULL,NULL,NULL),
	 (2,1,NULL,NULL,NULL,NULL,NULL),
	 (1,2,NULL,NULL,NULL,NULL,NULL),
	 (2,2,NULL,NULL,NULL,NULL,NULL);
INSERT INTO public."permission" (id_permission,name_permission) VALUES
	 (1,'admin.access'),
	 (2,'admin.dashboard.view.*'),
	 (3,'admin.dashboard.view.candidate'),
	 (4,'admin.dashboard.view.participant'),
	 (5,'admin.dashboard.view.tags'),
	 (6,'admin.dashboard.view.events'),
	 (7,'admin.dashboard.view.office'),
	 (8,'admin.dashboard.create.*'),
	 (9,'admin.dashboard.create.candidate'),
	 (11,'admin.dashboard.create.participant');
INSERT INTO public."permission" (id_permission,name_permission) VALUES
	 (12,'admin.dashboard.create.event'),
	 (13,'admin.dashboard.create.tag'),
	 (14,'admin.dashboard.create.office'),
	 (15,'*'),
	 (16,'candidate.dashboard'),
	 (17,'participant.dashboard'),
	 (18,'interviews.view'),
	 (19,'admin.edit.employee.password');
INSERT INTO public."role" (id_role,name_role) VALUES
	 (1,'superadmin'),
	 (2,'admin'),
	 (3,'employee'),
	 (4,'participant'),
	 (5,'candidate');
INSERT INTO public.role_permission (id_role,id_permission) VALUES
	 (1,15),
	 (2,1),
	 (2,2),
	 (2,8),
	 (3,1),
	 (3,2),
	 (3,9),
	 (3,11),
	 (3,12),
	 (3,13);
INSERT INTO public.role_permission (id_role,id_permission) VALUES
	 (1,17),
	 (2,17),
	 (3,17),
	 (4,17),
	 (1,16),
	 (2,16),
	 (3,16),
	 (5,16),
	 (5,18),
	 (4,18);
INSERT INTO public.role_permission (id_role,id_permission) VALUES
	 (1,19),
	 (2,19);
INSERT INTO public.tag (id_tag,name_tag) VALUES
	 (1,'SN2'),
	 (2,'SN2-C1'),
	 (3,'SN2-C2'),
	 (4,'SN1'),
	 (5,'SN1-C1'),
	 (6,'SN1-C2'),
	 (7,'M1');
INSERT INTO public.user_role (id_role,id_user) VALUES
	 (1,1),
	 (5,2),
	 (5,3),
	 (5,4),
	 (4,5),
	 (4,6),
	 (3,7);
