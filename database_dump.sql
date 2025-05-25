-- MySQL dump 10.13  Distrib 8.0.37, for Linux (x86_64)
--
-- Host: localhost    Database: graduation_projects
-- ------------------------------------------------------
-- Server version	8.0.37-0ubuntu0.20.04.3

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `announcement_announcement`
--

DROP TABLE IF EXISTS `announcement_announcement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `announcement_announcement` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `message` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `target_roles` json NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_by_id` bigint NOT NULL,
  `deadline` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `announcement_announc_created_by_id_f633b89a_fk_users_use` (`created_by_id`),
  CONSTRAINT `announcement_announc_created_by_id_f633b89a_fk_users_use` FOREIGN KEY (`created_by_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `announcement_announcement`
--

LOCK TABLES `announcement_announcement` WRITE;
/*!40000 ALTER TABLE `announcement_announcement` DISABLE KEYS */;
/*!40000 ALTER TABLE `announcement_announcement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `announcement_announcement_target_departments`
--

DROP TABLE IF EXISTS `announcement_announcement_target_departments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `announcement_announcement_target_departments` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `announcement_id` bigint NOT NULL,
  `department_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `announcement_announcemen_announcement_id_departme_f254b42a_uniq` (`announcement_id`,`department_id`),
  KEY `announcement_announc_department_id_97e03351_fk_universit` (`department_id`),
  CONSTRAINT `announcement_announc_announcement_id_93741a59_fk_announcem` FOREIGN KEY (`announcement_id`) REFERENCES `announcement_announcement` (`id`),
  CONSTRAINT `announcement_announc_department_id_97e03351_fk_universit` FOREIGN KEY (`department_id`) REFERENCES `university_department` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `announcement_announcement_target_departments`
--

LOCK TABLES `announcement_announcement_target_departments` WRITE;
/*!40000 ALTER TABLE `announcement_announcement_target_departments` DISABLE KEYS */;
/*!40000 ALTER TABLE `announcement_announcement_target_departments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `announcement_announcementfile`
--

DROP TABLE IF EXISTS `announcement_announcementfile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `announcement_announcementfile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file` varchar(100) NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `announcement_id` bigint NOT NULL,
  `uploaded_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `announcement_announc_announcement_id_0bc21685_fk_announcem` (`announcement_id`),
  KEY `announcement_announc_uploaded_by_id_51b66ee8_fk_users_use` (`uploaded_by_id`),
  CONSTRAINT `announcement_announc_announcement_id_0bc21685_fk_announcem` FOREIGN KEY (`announcement_id`) REFERENCES `announcement_announcement` (`id`),
  CONSTRAINT `announcement_announc_uploaded_by_id_51b66ee8_fk_users_use` FOREIGN KEY (`uploaded_by_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `announcement_announcementfile`
--

LOCK TABLES `announcement_announcementfile` WRITE;
/*!40000 ALTER TABLE `announcement_announcementfile` DISABLE KEYS */;
/*!40000 ALTER TABLE `announcement_announcementfile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=181 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add college',1,'add_college'),(2,'Can change college',1,'change_college'),(3,'Can delete college',1,'delete_college'),(4,'Can view college',1,'view_college'),(5,'Can add university',2,'add_university'),(6,'Can change university',2,'change_university'),(7,'Can delete university',2,'delete_university'),(8,'Can view university',2,'view_university'),(9,'Can add department',3,'add_department'),(10,'Can change department',3,'change_department'),(11,'Can delete department',3,'delete_department'),(12,'Can view department',3,'view_department'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add role',5,'add_role'),(18,'Can change role',5,'change_role'),(19,'Can delete role',5,'delete_role'),(20,'Can view role',5,'view_role'),(21,'Can add user',6,'add_admin'),(22,'Can change user',6,'change_admin'),(23,'Can delete user',6,'delete_admin'),(24,'Can view user',6,'view_admin'),(25,'Can add user',7,'add_coordinator'),(26,'Can change user',7,'change_coordinator'),(27,'Can delete user',7,'delete_coordinator'),(28,'Can view user',7,'view_coordinator'),(29,'Can add user',8,'add_student'),(30,'Can change user',8,'change_student'),(31,'Can delete user',8,'delete_student'),(32,'Can view user',8,'view_student'),(33,'Can add user',9,'add_supervisor'),(34,'Can change user',9,'change_supervisor'),(35,'Can delete user',9,'delete_supervisor'),(36,'Can view user',9,'view_supervisor'),(37,'Can add user creation log',10,'add_usercreationlog'),(38,'Can change user creation log',10,'change_usercreationlog'),(39,'Can delete user creation log',10,'delete_usercreationlog'),(40,'Can view user creation log',10,'view_usercreationlog'),(41,'Can add annual grade',11,'add_annualgrade'),(42,'Can change annual grade',11,'change_annualgrade'),(43,'Can delete annual grade',11,'delete_annualgrade'),(44,'Can view annual grade',11,'view_annualgrade'),(45,'Can add feedback exchange',12,'add_feedbackexchange'),(46,'Can change feedback exchange',12,'change_feedbackexchange'),(47,'Can delete feedback exchange',12,'delete_feedbackexchange'),(48,'Can view feedback exchange',12,'view_feedbackexchange'),(49,'Can add project',13,'add_project'),(50,'Can change project',13,'change_project'),(51,'Can delete project',13,'delete_project'),(52,'Can view project',13,'view_project'),(53,'Can add project goal',14,'add_projectgoal'),(54,'Can change project goal',14,'change_projectgoal'),(55,'Can delete project goal',14,'delete_projectgoal'),(56,'Can view project goal',14,'view_projectgoal'),(57,'Can add project log',15,'add_projectlog'),(58,'Can change project log',15,'change_projectlog'),(59,'Can delete project log',15,'delete_projectlog'),(60,'Can view project log',15,'view_projectlog'),(61,'Can add project membership',16,'add_projectmembership'),(62,'Can change project membership',16,'change_projectmembership'),(63,'Can delete project membership',16,'delete_projectmembership'),(64,'Can view project membership',16,'view_projectmembership'),(65,'Can add project plan',17,'add_projectplan'),(66,'Can change project plan',17,'change_projectplan'),(67,'Can delete project plan',17,'delete_projectplan'),(68,'Can view project plan',17,'view_projectplan'),(69,'Can add project proposal',18,'add_projectproposal'),(70,'Can change project proposal',18,'change_projectproposal'),(71,'Can delete project proposal',18,'delete_projectproposal'),(72,'Can view project proposal',18,'view_projectproposal'),(73,'Can add project task',19,'add_projecttask'),(74,'Can change project task',19,'change_projecttask'),(75,'Can delete project task',19,'delete_projecttask'),(76,'Can view project task',19,'view_projecttask'),(77,'Can add student project membership',20,'add_studentprojectmembership'),(78,'Can change student project membership',20,'change_studentprojectmembership'),(79,'Can delete student project membership',20,'delete_studentprojectmembership'),(80,'Can view student project membership',20,'view_studentprojectmembership'),(81,'Can add available time',21,'add_availabletime'),(82,'Can change available time',21,'change_availabletime'),(83,'Can delete available time',21,'delete_availabletime'),(84,'Can view available time',21,'view_availabletime'),(85,'Can add meeting',22,'add_meeting'),(86,'Can change meeting',22,'change_meeting'),(87,'Can delete meeting',22,'delete_meeting'),(88,'Can view meeting',22,'view_meeting'),(89,'Can add meeting file',23,'add_meetingfile'),(90,'Can change meeting file',23,'change_meetingfile'),(91,'Can delete meeting file',23,'delete_meetingfile'),(92,'Can view meeting file',23,'view_meetingfile'),(93,'Can add meeting participant',24,'add_meetingparticipant'),(94,'Can change meeting participant',24,'change_meetingparticipant'),(95,'Can delete meeting participant',24,'delete_meetingparticipant'),(96,'Can view meeting participant',24,'view_meetingparticipant'),(97,'Can add project report',25,'add_projectreport'),(98,'Can change project report',25,'change_projectreport'),(99,'Can delete project report',25,'delete_projectreport'),(100,'Can view project report',25,'view_projectreport'),(101,'Can add team member status',26,'add_teammemberstatus'),(102,'Can change team member status',26,'change_teammemberstatus'),(103,'Can delete team member status',26,'delete_teammemberstatus'),(104,'Can view team member status',26,'view_teammemberstatus'),(105,'Can add notification',27,'add_notification'),(106,'Can change notification',27,'change_notification'),(107,'Can delete notification',27,'delete_notification'),(108,'Can view notification',27,'view_notification'),(109,'Can add evaluation form',28,'add_evaluationform'),(110,'Can change evaluation form',28,'change_evaluationform'),(111,'Can delete evaluation form',28,'delete_evaluationform'),(112,'Can view evaluation form',28,'view_evaluationform'),(113,'Can add main category',29,'add_maincategory'),(114,'Can change main category',29,'change_maincategory'),(115,'Can delete main category',29,'delete_maincategory'),(116,'Can view main category',29,'view_maincategory'),(117,'Can add sub category',30,'add_subcategory'),(118,'Can change sub category',30,'change_subcategory'),(119,'Can delete sub category',30,'delete_subcategory'),(120,'Can view sub category',30,'view_subcategory'),(121,'Can add grade',31,'add_grade'),(122,'Can change grade',31,'change_grade'),(123,'Can delete grade',31,'delete_grade'),(124,'Can view grade',31,'view_grade'),(125,'Can add grading',32,'add_grading'),(126,'Can change grading',32,'change_grading'),(127,'Can delete grading',32,'delete_grading'),(128,'Can view grading',32,'view_grading'),(129,'Can add individual grade',33,'add_individualgrade'),(130,'Can change individual grade',33,'change_individualgrade'),(131,'Can delete individual grade',33,'delete_individualgrade'),(132,'Can view individual grade',33,'view_individualgrade'),(133,'Can add member grade',34,'add_membergrade'),(134,'Can change member grade',34,'change_membergrade'),(135,'Can delete member grade',34,'delete_membergrade'),(136,'Can view member grade',34,'view_membergrade'),(137,'Can add member individual grade',35,'add_memberindividualgrade'),(138,'Can change member individual grade',35,'change_memberindividualgrade'),(139,'Can delete member individual grade',35,'delete_memberindividualgrade'),(140,'Can view member individual grade',35,'view_memberindividualgrade'),(141,'Can add feedback file',36,'add_feedbackfile'),(142,'Can change feedback file',36,'change_feedbackfile'),(143,'Can delete feedback file',36,'delete_feedbackfile'),(144,'Can view feedback file',36,'view_feedbackfile'),(145,'Can add feedback reply',37,'add_feedbackreply'),(146,'Can change feedback reply',37,'change_feedbackreply'),(147,'Can delete feedback reply',37,'delete_feedbackreply'),(148,'Can view feedback reply',37,'view_feedbackreply'),(149,'Can add project feedback',38,'add_projectfeedback'),(150,'Can change project feedback',38,'change_projectfeedback'),(151,'Can delete project feedback',38,'delete_projectfeedback'),(152,'Can view project feedback',38,'view_projectfeedback'),(153,'Can add log entry',39,'add_logentry'),(154,'Can change log entry',39,'change_logentry'),(155,'Can delete log entry',39,'delete_logentry'),(156,'Can view log entry',39,'view_logentry'),(157,'Can add permission',40,'add_permission'),(158,'Can change permission',40,'change_permission'),(159,'Can delete permission',40,'delete_permission'),(160,'Can view permission',40,'view_permission'),(161,'Can add group',41,'add_group'),(162,'Can change group',41,'change_group'),(163,'Can delete group',41,'delete_group'),(164,'Can view group',41,'view_group'),(165,'Can add content type',42,'add_contenttype'),(166,'Can change content type',42,'change_contenttype'),(167,'Can delete content type',42,'delete_contenttype'),(168,'Can view content type',42,'view_contenttype'),(169,'Can add session',43,'add_session'),(170,'Can change session',43,'change_session'),(171,'Can delete session',43,'delete_session'),(172,'Can view session',43,'view_session'),(173,'Can add announcement',44,'add_announcement'),(174,'Can change announcement',44,'change_announcement'),(175,'Can delete announcement',44,'delete_announcement'),(176,'Can view announcement',44,'view_announcement'),(177,'Can add announcement file',45,'add_announcementfile'),(178,'Can change announcement file',45,'change_announcementfile'),(179,'Can delete announcement file',45,'delete_announcementfile'),(180,'Can view announcement file',45,'view_announcementfile');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_users_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2025-05-18 17:27:48.446544','1','Sudan University of Science and Technology',1,'[{\"added\": {}}]',2,2),(2,'2025-05-19 18:15:17.199476','1','Supervisor',1,'[{\"added\": {}}]',5,2),(3,'2025-05-19 18:15:21.698828','2','Reader',1,'[{\"added\": {}}]',5,2),(4,'2025-05-19 18:15:30.912287','3','Judgement Committee',1,'[{\"added\": {}}]',5,2),(5,'2025-05-19 18:15:36.012628','4','Coordinator',1,'[{\"added\": {}}]',5,2),(6,'2025-05-19 18:39:15.316539','3','project 2',3,'',13,2),(7,'2025-05-20 20:45:46.365868','9','Coordinator: malik',2,'[]',7,2),(8,'2025-05-22 18:44:54.775701','22','StudentProjectMembership object (22)',3,'',20,2),(9,'2025-05-22 18:44:54.888857','15','StudentProjectMembership object (15)',3,'',20,2),(10,'2025-05-22 18:44:55.003728','14','StudentProjectMembership object (14)',3,'',20,2),(11,'2025-05-22 18:44:55.151426','13','StudentProjectMembership object (13)',3,'',20,2),(12,'2025-05-25 20:16:05.812480','4','project 2',3,'',13,2),(13,'2025-05-25 20:16:05.872139','5','project 3',3,'',13,2),(14,'2025-05-25 20:16:05.925067','7','re2',3,'',13,2),(15,'2025-05-25 20:16:05.975764','1','Sudan Mental Health App',3,'',13,2),(16,'2025-05-25 20:16:17.792220','8','ProjectProposal object (8)',3,'',18,2),(17,'2025-05-25 20:16:17.846502','7','ProjectProposal object (7)',3,'',18,2),(18,'2025-05-25 20:16:17.905537','4','ProjectProposal object (4)',3,'',18,2),(19,'2025-05-25 20:16:17.978114','1','ProjectProposal object (1)',3,'',18,2);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (39,'admin','logentry'),(44,'announcement','announcement'),(45,'announcement','announcementfile'),(41,'auth','group'),(40,'auth','permission'),(42,'contenttypes','contenttype'),(36,'feedbacks','feedbackfile'),(37,'feedbacks','feedbackreply'),(38,'feedbacks','projectfeedback'),(28,'form','evaluationform'),(29,'form','maincategory'),(30,'form','subcategory'),(31,'grades','grade'),(32,'grades','grading'),(33,'grades','individualgrade'),(34,'grades','membergrade'),(35,'grades','memberindividualgrade'),(21,'meeting','availabletime'),(22,'meeting','meeting'),(23,'meeting','meetingfile'),(24,'meeting','meetingparticipant'),(27,'notifications','notification'),(11,'project','annualgrade'),(12,'project','feedbackexchange'),(13,'project','project'),(14,'project','projectgoal'),(15,'project','projectlog'),(16,'project','projectmembership'),(17,'project','projectplan'),(18,'project','projectproposal'),(19,'project','projecttask'),(20,'project','studentprojectmembership'),(25,'report','projectreport'),(26,'report','teammemberstatus'),(43,'sessions','session'),(1,'university','college'),(3,'university','department'),(2,'university','university'),(6,'users','admin'),(7,'users','coordinator'),(5,'users','role'),(8,'users','student'),(9,'users','supervisor'),(4,'users','user'),(10,'users','usercreationlog');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'university','0001_initial','2025-05-18 12:36:26.500256'),(2,'contenttypes','0001_initial','2025-05-18 12:36:26.805385'),(3,'contenttypes','0002_remove_content_type_name','2025-05-18 12:36:27.222493'),(4,'auth','0001_initial','2025-05-18 12:36:29.239281'),(5,'auth','0002_alter_permission_name_max_length','2025-05-18 12:36:29.725105'),(6,'auth','0003_alter_user_email_max_length','2025-05-18 12:36:29.749868'),(7,'auth','0004_alter_user_username_opts','2025-05-18 12:36:29.780823'),(8,'auth','0005_alter_user_last_login_null','2025-05-18 12:36:29.809049'),(9,'auth','0006_require_contenttypes_0002','2025-05-18 12:36:29.832175'),(10,'auth','0007_alter_validators_add_error_messages','2025-05-18 12:36:29.859108'),(11,'auth','0008_alter_user_username_max_length','2025-05-18 12:36:29.886283'),(12,'auth','0009_alter_user_last_name_max_length','2025-05-18 12:36:29.921698'),(13,'auth','0010_alter_group_name_max_length','2025-05-18 12:36:30.004982'),(14,'auth','0011_update_proxy_permissions','2025-05-18 12:36:30.043203'),(15,'auth','0012_alter_user_first_name_max_length','2025-05-18 12:36:30.066645'),(16,'users','0001_initial','2025-05-18 12:36:36.581802'),(17,'admin','0001_initial','2025-05-18 12:36:37.671557'),(18,'admin','0002_logentry_remove_auto_add','2025-05-18 12:36:37.709021'),(19,'admin','0003_logentry_add_action_flag_choices','2025-05-18 12:36:37.741552'),(20,'project','0001_initial','2025-05-18 12:36:40.393328'),(21,'feedbacks','0001_initial','2025-05-18 12:36:40.914390'),(22,'feedbacks','0002_initial','2025-05-18 12:36:41.341390'),(23,'feedbacks','0003_initial','2025-05-18 12:36:43.653117'),(24,'form','0001_initial','2025-05-18 12:36:45.263531'),(25,'form','0002_initial','2025-05-18 12:36:46.937556'),(26,'grades','0001_initial','2025-05-18 12:36:48.205434'),(27,'grades','0002_initial','2025-05-18 12:36:55.241051'),(28,'meeting','0001_initial','2025-05-18 12:36:56.428569'),(29,'meeting','0002_initial','2025-05-18 12:37:00.264156'),(30,'notifications','0001_initial','2025-05-18 12:37:00.483005'),(31,'notifications','0002_initial','2025-05-18 12:37:01.261940'),(32,'project','0002_initial','2025-05-18 12:37:17.913617'),(33,'project','0003_project_research_file_and_more','2025-05-18 12:37:18.370484'),(34,'project','0004_feedbackexchange_task','2025-05-18 12:37:18.969604'),(35,'report','0001_initial','2025-05-18 12:37:19.401604'),(36,'report','0002_initial','2025-05-18 12:37:24.077677'),(37,'report','0003_projectreport_teammemberstatus_and_more','2025-05-18 12:37:27.973300'),(38,'sessions','0001_initial','2025-05-18 12:37:28.319313'),(39,'feedbacks','0004_alter_feedbackfile_feedback_alter_feedbackfile_file_and_more','2025-05-20 17:48:35.964989'),(40,'university','0002_alter_college_location_alter_college_name_and_more','2025-05-20 17:48:36.114640'),(41,'users','0002_alter_coordinator_coord_id_and_more','2025-05-20 17:48:36.516748'),(42,'form','0003_alter_evaluationform_coordinators_and_more','2025-05-20 17:48:36.758689'),(43,'grades','0003_alter_membergrade_options_and_more','2025-05-20 17:48:37.307246'),(44,'meeting','0003_alter_availabletime_options_alter_availabletime_day_and_more','2025-05-20 17:48:37.916993'),(45,'project','0005_alter_annualgrade_options_and_more','2025-05-20 17:48:41.014373'),(46,'report','0004_alter_teammemberstatus_options_and_more','2025-05-20 17:48:41.408345'),(47,'project','0006_projectmembership_proposal','2025-05-20 21:42:20.945968'),(48,'project','0007_remove_projectmembership_proposal_and_more','2025-05-20 22:00:29.058490'),(49,'announcement','0001_initial','2025-05-25 19:21:54.488759'),(50,'announcement','0002_announcement_deadline','2025-05-25 19:21:54.677479'),(51,'announcement','0003_announcementfile','2025-05-25 19:21:55.609904'),(52,'announcement','0004_remove_announcement_attachment','2025-05-25 19:21:55.779762');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('2zamwafbe31u0fl6l8wusyvi8yladsby','.eJxVjDsOwjAQBe_iGllrb-zElPQ5Q7Rrr3EAOVI-FeLuJFIKaN_MvLcaaFvLsC0yD2NSV2XV5Xdjik-pB0gPqvdJx6mu88j6UPRJF91PSV630_07KLSUvQbJHYpBJw169sm50ACAbW1ngzAiUUATE-xCbBgImHIM3EZvnKesPl_J7Te6:1uJJeA:db7jF0BWCc_0yVv50pA0HvhAi3v3V7URzlomiCsR1yE','2025-06-08 22:16:46.268264'),('n4c3ojp33j6ittz5jkqt2kbrv0p9sqt7','.eJxVjM0OwiAQhN-FsyEsK6V49O4zkF1-pGogKe3J-O62SQ96mmS-b-YtPK1L8WtPs5-iuAhQ4vRbMoVnqjuJD6r3JkOryzyx3BV50C5vLabX9XD_Dgr1sq0xJe3GwAgqniE4ow0xOkZtIVmDY1QWwoDMlDMrk7cMoFhrx5BxEJ8vA004RQ:1uJGOk:96E5sS8TB-M6V7NJSyQGwFhI5M02zmWcPgLt9uJ8M7k','2025-06-08 18:48:38.824617');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feedbacks_feedbackfile`
--

DROP TABLE IF EXISTS `feedbacks_feedbackfile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedbacks_feedbackfile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file` varchar(100) NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `feedback_id` bigint NOT NULL,
  `reply_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `feedbacks_feedbackfi_feedback_id_da6ece5b_fk_feedbacks` (`feedback_id`),
  KEY `feedbacks_feedbackfi_reply_id_821ee74c_fk_feedbacks` (`reply_id`),
  CONSTRAINT `feedbacks_feedbackfi_feedback_id_da6ece5b_fk_feedbacks` FOREIGN KEY (`feedback_id`) REFERENCES `feedbacks_projectfeedback` (`id`),
  CONSTRAINT `feedbacks_feedbackfi_reply_id_821ee74c_fk_feedbacks` FOREIGN KEY (`reply_id`) REFERENCES `feedbacks_feedbackreply` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feedbacks_feedbackfile`
--

LOCK TABLES `feedbacks_feedbackfile` WRITE;
/*!40000 ALTER TABLE `feedbacks_feedbackfile` DISABLE KEYS */;
/*!40000 ALTER TABLE `feedbacks_feedbackfile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feedbacks_feedbackreply`
--

DROP TABLE IF EXISTS `feedbacks_feedbackreply`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedbacks_feedbackreply` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `message` longtext,
  `created_at` datetime(6) NOT NULL,
  `feedback_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `feedback_id` (`feedback_id`),
  CONSTRAINT `feedbacks_feedbackre_feedback_id_5379e56d_fk_feedbacks` FOREIGN KEY (`feedback_id`) REFERENCES `feedbacks_projectfeedback` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feedbacks_feedbackreply`
--

LOCK TABLES `feedbacks_feedbackreply` WRITE;
/*!40000 ALTER TABLE `feedbacks_feedbackreply` DISABLE KEYS */;
/*!40000 ALTER TABLE `feedbacks_feedbackreply` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feedbacks_projectfeedback`
--

DROP TABLE IF EXISTS `feedbacks_projectfeedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedbacks_projectfeedback` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `message` longtext,
  `created_at` datetime(6) NOT NULL,
  `project_id` bigint NOT NULL,
  `sender_id` bigint NOT NULL,
  `teacher_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `feedbacks_projectfee_project_id_b8131128_fk_project_p` (`project_id`),
  KEY `feedbacks_projectfeedback_sender_id_b2609bf6_fk_users_user_id` (`sender_id`),
  KEY `feedbacks_projectfeedback_teacher_id_749220de_fk_users_user_id` (`teacher_id`),
  CONSTRAINT `feedbacks_projectfee_project_id_b8131128_fk_project_p` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`),
  CONSTRAINT `feedbacks_projectfeedback_sender_id_b2609bf6_fk_users_user_id` FOREIGN KEY (`sender_id`) REFERENCES `users_user` (`id`),
  CONSTRAINT `feedbacks_projectfeedback_teacher_id_749220de_fk_users_user_id` FOREIGN KEY (`teacher_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feedbacks_projectfeedback`
--

LOCK TABLES `feedbacks_projectfeedback` WRITE;
/*!40000 ALTER TABLE `feedbacks_projectfeedback` DISABLE KEYS */;
/*!40000 ALTER TABLE `feedbacks_projectfeedback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `form_evaluationform`
--

DROP TABLE IF EXISTS `form_evaluationform`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `form_evaluationform` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `form_weight` double NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `target_role_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `form_evaluationform_target_role_id_9cb09787_fk_users_role_id` (`target_role_id`),
  CONSTRAINT `form_evaluationform_target_role_id_9cb09787_fk_users_role_id` FOREIGN KEY (`target_role_id`) REFERENCES `users_role` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `form_evaluationform`
--

LOCK TABLES `form_evaluationform` WRITE;
/*!40000 ALTER TABLE `form_evaluationform` DISABLE KEYS */;
/*!40000 ALTER TABLE `form_evaluationform` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `form_evaluationform_coordinators`
--

DROP TABLE IF EXISTS `form_evaluationform_coordinators`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `form_evaluationform_coordinators` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `evaluationform_id` bigint NOT NULL,
  `coordinator_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `form_evaluationform_coor_evaluationform_id_coordi_3071adce_uniq` (`evaluationform_id`,`coordinator_id`),
  KEY `form_evaluationform__coordinator_id_ae9065f5_fk_users_coo` (`coordinator_id`),
  CONSTRAINT `form_evaluationform__coordinator_id_ae9065f5_fk_users_coo` FOREIGN KEY (`coordinator_id`) REFERENCES `users_coordinator` (`user_ptr_id`),
  CONSTRAINT `form_evaluationform__evaluationform_id_8051753f_fk_form_eval` FOREIGN KEY (`evaluationform_id`) REFERENCES `form_evaluationform` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `form_evaluationform_coordinators`
--

LOCK TABLES `form_evaluationform_coordinators` WRITE;
/*!40000 ALTER TABLE `form_evaluationform_coordinators` DISABLE KEYS */;
/*!40000 ALTER TABLE `form_evaluationform_coordinators` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `form_maincategory`
--

DROP TABLE IF EXISTS `form_maincategory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `form_maincategory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `number` int unsigned NOT NULL,
  `text` longtext NOT NULL,
  `weight` double NOT NULL,
  `grade_type` varchar(20) NOT NULL,
  `evaluation_form_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `form_maincategory_evaluation_form_id_b46d2963_fk_form_eval` (`evaluation_form_id`),
  CONSTRAINT `form_maincategory_evaluation_form_id_b46d2963_fk_form_eval` FOREIGN KEY (`evaluation_form_id`) REFERENCES `form_evaluationform` (`id`),
  CONSTRAINT `form_maincategory_chk_1` CHECK ((`number` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `form_maincategory`
--

LOCK TABLES `form_maincategory` WRITE;
/*!40000 ALTER TABLE `form_maincategory` DISABLE KEYS */;
/*!40000 ALTER TABLE `form_maincategory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `form_subcategory`
--

DROP TABLE IF EXISTS `form_subcategory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `form_subcategory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `text` longtext NOT NULL,
  `main_category_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `form_subcategory_main_category_id_223d89b0_fk_form_main` (`main_category_id`),
  CONSTRAINT `form_subcategory_main_category_id_223d89b0_fk_form_main` FOREIGN KEY (`main_category_id`) REFERENCES `form_maincategory` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `form_subcategory`
--

LOCK TABLES `form_subcategory` WRITE;
/*!40000 ALTER TABLE `form_subcategory` DISABLE KEYS */;
/*!40000 ALTER TABLE `form_subcategory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grades_grade`
--

DROP TABLE IF EXISTS `grades_grade`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grades_grade` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `grade` double NOT NULL,
  `final_grade` double NOT NULL,
  `evaluation_form_id` bigint NOT NULL,
  `main_category_id` bigint NOT NULL,
  `project_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `grades_grade_evaluation_form_id_161761a2_fk_form_eval` (`evaluation_form_id`),
  KEY `grades_grade_main_category_id_554f0247_fk_form_maincategory_id` (`main_category_id`),
  KEY `grades_grade_project_id_03f10968_fk_project_project_id` (`project_id`),
  CONSTRAINT `grades_grade_evaluation_form_id_161761a2_fk_form_eval` FOREIGN KEY (`evaluation_form_id`) REFERENCES `form_evaluationform` (`id`),
  CONSTRAINT `grades_grade_main_category_id_554f0247_fk_form_maincategory_id` FOREIGN KEY (`main_category_id`) REFERENCES `form_maincategory` (`id`),
  CONSTRAINT `grades_grade_project_id_03f10968_fk_project_project_id` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grades_grade`
--

LOCK TABLES `grades_grade` WRITE;
/*!40000 ALTER TABLE `grades_grade` DISABLE KEYS */;
/*!40000 ALTER TABLE `grades_grade` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grades_grading`
--

DROP TABLE IF EXISTS `grades_grading`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grades_grading` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `final_grade` double NOT NULL,
  `is_sent` tinyint(1) NOT NULL,
  `project_id` bigint NOT NULL,
  `student_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `grades_grading_project_id_d9e3cf22_fk_project_project_id` (`project_id`),
  KEY `grades_grading_student_id_6c1b0ce9_fk_users_student_user_ptr_id` (`student_id`),
  CONSTRAINT `grades_grading_project_id_d9e3cf22_fk_project_project_id` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`),
  CONSTRAINT `grades_grading_student_id_6c1b0ce9_fk_users_student_user_ptr_id` FOREIGN KEY (`student_id`) REFERENCES `users_student` (`user_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grades_grading`
--

LOCK TABLES `grades_grading` WRITE;
/*!40000 ALTER TABLE `grades_grading` DISABLE KEYS */;
/*!40000 ALTER TABLE `grades_grading` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grades_individualgrade`
--

DROP TABLE IF EXISTS `grades_individualgrade`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grades_individualgrade` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `final_grade` double NOT NULL,
  `evaluation_form_id` bigint NOT NULL,
  `grade_id` bigint NOT NULL,
  `student_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `grades_individualgra_evaluation_form_id_31cba3e9_fk_form_eval` (`evaluation_form_id`),
  KEY `grades_individualgrade_grade_id_99c55616_fk_grades_grade_id` (`grade_id`),
  KEY `grades_individualgra_student_id_eb6152df_fk_users_stu` (`student_id`),
  CONSTRAINT `grades_individualgra_evaluation_form_id_31cba3e9_fk_form_eval` FOREIGN KEY (`evaluation_form_id`) REFERENCES `form_evaluationform` (`id`),
  CONSTRAINT `grades_individualgra_student_id_eb6152df_fk_users_stu` FOREIGN KEY (`student_id`) REFERENCES `users_student` (`user_ptr_id`),
  CONSTRAINT `grades_individualgrade_grade_id_99c55616_fk_grades_grade_id` FOREIGN KEY (`grade_id`) REFERENCES `grades_grade` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grades_individualgrade`
--

LOCK TABLES `grades_individualgrade` WRITE;
/*!40000 ALTER TABLE `grades_individualgrade` DISABLE KEYS */;
/*!40000 ALTER TABLE `grades_individualgrade` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grades_membergrade`
--

DROP TABLE IF EXISTS `grades_membergrade`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grades_membergrade` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `grade_id` bigint NOT NULL,
  `member_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `grades_membergrade_member_id_grade_id_3fe47220_uniq` (`member_id`,`grade_id`),
  KEY `grades_membergrade_grade_id_b31156ee_fk_grades_grade_id` (`grade_id`),
  CONSTRAINT `grades_membergrade_grade_id_b31156ee_fk_grades_grade_id` FOREIGN KEY (`grade_id`) REFERENCES `grades_grade` (`id`),
  CONSTRAINT `grades_membergrade_member_id_79af3124_fk_users_user_id` FOREIGN KEY (`member_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grades_membergrade`
--

LOCK TABLES `grades_membergrade` WRITE;
/*!40000 ALTER TABLE `grades_membergrade` DISABLE KEYS */;
/*!40000 ALTER TABLE `grades_membergrade` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grades_memberindividualgrade`
--

DROP TABLE IF EXISTS `grades_memberindividualgrade`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grades_memberindividualgrade` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `individual_grade_id` bigint NOT NULL,
  `member_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `grades_memberindividualg_member_id_individual_gra_eb3010f6_uniq` (`member_id`,`individual_grade_id`),
  KEY `grades_memberindivid_individual_grade_id_2135a73f_fk_grades_in` (`individual_grade_id`),
  CONSTRAINT `grades_memberindivid_individual_grade_id_2135a73f_fk_grades_in` FOREIGN KEY (`individual_grade_id`) REFERENCES `grades_individualgrade` (`id`),
  CONSTRAINT `grades_memberindividualgrade_member_id_57d88b01_fk_users_user_id` FOREIGN KEY (`member_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grades_memberindividualgrade`
--

LOCK TABLES `grades_memberindividualgrade` WRITE;
/*!40000 ALTER TABLE `grades_memberindividualgrade` DISABLE KEYS */;
/*!40000 ALTER TABLE `grades_memberindividualgrade` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `meeting_availabletime`
--

DROP TABLE IF EXISTS `meeting_availabletime`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meeting_availabletime` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `day` varchar(3) NOT NULL,
  `start_time` time(6) NOT NULL,
  `end_time` time(6) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `meeting_availabletime_user_id_day_start_time_e_97476060_uniq` (`user_id`,`day`,`start_time`,`end_time`),
  CONSTRAINT `meeting_availabletime_user_id_3fb7a089_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meeting_availabletime`
--

LOCK TABLES `meeting_availabletime` WRITE;
/*!40000 ALTER TABLE `meeting_availabletime` DISABLE KEYS */;
/*!40000 ALTER TABLE `meeting_availabletime` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `meeting_meeting`
--

DROP TABLE IF EXISTS `meeting_meeting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meeting_meeting` (
  `meeting_id` int NOT NULL AUTO_INCREMENT,
  `start_datetime` datetime(6) NOT NULL,
  `end_datetime` datetime(6) NOT NULL,
  `status` varchar(20) NOT NULL,
  `comment` longtext,
  `recommendation` longtext,
  `meeting_report` longtext,
  `created_at` datetime(6) NOT NULL,
  `project_id` bigint DEFAULT NULL,
  `requested_by_id` bigint NOT NULL,
  `teacher_id` bigint NOT NULL,
  PRIMARY KEY (`meeting_id`),
  KEY `meeting_meeting_project_id_8146318e_fk_project_project_id` (`project_id`),
  KEY `meeting_meeting_requested_by_id_3bd25286_fk_users_user_id` (`requested_by_id`),
  KEY `meeting_meeting_teacher_id_80a91ca7_fk_users_user_id` (`teacher_id`),
  CONSTRAINT `meeting_meeting_project_id_8146318e_fk_project_project_id` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`),
  CONSTRAINT `meeting_meeting_requested_by_id_3bd25286_fk_users_user_id` FOREIGN KEY (`requested_by_id`) REFERENCES `users_user` (`id`),
  CONSTRAINT `meeting_meeting_teacher_id_80a91ca7_fk_users_user_id` FOREIGN KEY (`teacher_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meeting_meeting`
--

LOCK TABLES `meeting_meeting` WRITE;
/*!40000 ALTER TABLE `meeting_meeting` DISABLE KEYS */;
/*!40000 ALTER TABLE `meeting_meeting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `meeting_meetingfile`
--

DROP TABLE IF EXISTS `meeting_meetingfile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meeting_meetingfile` (
  `file_id` int NOT NULL AUTO_INCREMENT,
  `file` varchar(100) NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `description` longtext,
  `meeting_id` int NOT NULL,
  `uploaded_by_id` bigint NOT NULL,
  PRIMARY KEY (`file_id`),
  KEY `meeting_meetingfile_meeting_id_6b460cb1_fk_meeting_m` (`meeting_id`),
  KEY `meeting_meetingfile_uploaded_by_id_65a3042d_fk_users_user_id` (`uploaded_by_id`),
  CONSTRAINT `meeting_meetingfile_meeting_id_6b460cb1_fk_meeting_m` FOREIGN KEY (`meeting_id`) REFERENCES `meeting_meeting` (`meeting_id`),
  CONSTRAINT `meeting_meetingfile_uploaded_by_id_65a3042d_fk_users_user_id` FOREIGN KEY (`uploaded_by_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meeting_meetingfile`
--

LOCK TABLES `meeting_meetingfile` WRITE;
/*!40000 ALTER TABLE `meeting_meetingfile` DISABLE KEYS */;
/*!40000 ALTER TABLE `meeting_meetingfile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `meeting_meetingparticipant`
--

DROP TABLE IF EXISTS `meeting_meetingparticipant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meeting_meetingparticipant` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `attendance_status` varchar(10) NOT NULL,
  `has_accepted` tinyint(1) NOT NULL,
  `meeting_id` int NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `meeting_meetingparti_meeting_id_5a5f0314_fk_meeting_m` (`meeting_id`),
  KEY `meeting_meetingparticipant_user_id_31ce17bd_fk_users_user_id` (`user_id`),
  CONSTRAINT `meeting_meetingparti_meeting_id_5a5f0314_fk_meeting_m` FOREIGN KEY (`meeting_id`) REFERENCES `meeting_meeting` (`meeting_id`),
  CONSTRAINT `meeting_meetingparticipant_user_id_31ce17bd_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meeting_meetingparticipant`
--

LOCK TABLES `meeting_meetingparticipant` WRITE;
/*!40000 ALTER TABLE `meeting_meetingparticipant` DISABLE KEYS */;
/*!40000 ALTER TABLE `meeting_meetingparticipant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications_notification`
--

DROP TABLE IF EXISTS `notifications_notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications_notification` (
  `id` char(32) NOT NULL,
  `message` longtext NOT NULL,
  `notification_type` varchar(50) NOT NULL,
  `sent_at` datetime(6) NOT NULL,
  `read` tinyint(1) NOT NULL,
  `recipient_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `notifications_notifi_recipient_id_d055f3f0_fk_users_use` (`recipient_id`),
  CONSTRAINT `notifications_notifi_recipient_id_d055f3f0_fk_users_use` FOREIGN KEY (`recipient_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications_notification`
--

LOCK TABLES `notifications_notification` WRITE;
/*!40000 ALTER TABLE `notifications_notification` DISABLE KEYS */;
/*!40000 ALTER TABLE `notifications_notification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_annualgrade`
--

DROP TABLE IF EXISTS `project_annualgrade`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_annualgrade` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `grade` double NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `project_id` bigint NOT NULL,
  `student_id` bigint NOT NULL,
  `supervisor_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_annualgrade_supervisor_id_student_id_175610f2_uniq` (`supervisor_id`,`student_id`,`project_id`),
  KEY `project_annualgrade_project_id_dae20171_fk_project_project_id` (`project_id`),
  KEY `project_annualgrade_student_id_d96f2093_fk_users_user_id` (`student_id`),
  CONSTRAINT `project_annualgrade_project_id_dae20171_fk_project_project_id` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`),
  CONSTRAINT `project_annualgrade_student_id_d96f2093_fk_users_user_id` FOREIGN KEY (`student_id`) REFERENCES `users_user` (`id`),
  CONSTRAINT `project_annualgrade_supervisor_id_0fa75e5c_fk_users_sup` FOREIGN KEY (`supervisor_id`) REFERENCES `users_supervisor` (`user_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_annualgrade`
--

LOCK TABLES `project_annualgrade` WRITE;
/*!40000 ALTER TABLE `project_annualgrade` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_annualgrade` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_feedbackexchange`
--

DROP TABLE IF EXISTS `project_feedbackexchange`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_feedbackexchange` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `feedback_text` longtext,
  `feedback_file` varchar(100) DEFAULT NULL,
  `comment` longtext,
  `created_at` datetime(6) NOT NULL,
  `project_id` bigint DEFAULT NULL,
  `proposal_id` bigint DEFAULT NULL,
  `receiver_id` bigint DEFAULT NULL,
  `sender_id` bigint NOT NULL,
  `task_id` bigint DEFAULT NULL,
  `report_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `project_feedbackexch_project_id_11708871_fk_project_p` (`project_id`),
  KEY `project_feedbackexch_proposal_id_c6967ab2_fk_project_p` (`proposal_id`),
  KEY `project_feedbackexchange_receiver_id_51cdbb02_fk_users_user_id` (`receiver_id`),
  KEY `project_feedbackexchange_sender_id_a8f5bf0d_fk_users_user_id` (`sender_id`),
  KEY `project_feedbackexch_task_id_42ebccf3_fk_project_p` (`task_id`),
  KEY `project_feedbackexch_report_id_58d4215e_fk_report_pr` (`report_id`),
  CONSTRAINT `project_feedbackexch_project_id_11708871_fk_project_p` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`),
  CONSTRAINT `project_feedbackexch_proposal_id_c6967ab2_fk_project_p` FOREIGN KEY (`proposal_id`) REFERENCES `project_projectproposal` (`id`),
  CONSTRAINT `project_feedbackexch_report_id_58d4215e_fk_report_pr` FOREIGN KEY (`report_id`) REFERENCES `report_projectreport` (`id`),
  CONSTRAINT `project_feedbackexch_task_id_42ebccf3_fk_project_p` FOREIGN KEY (`task_id`) REFERENCES `project_projecttask` (`id`),
  CONSTRAINT `project_feedbackexchange_receiver_id_51cdbb02_fk_users_user_id` FOREIGN KEY (`receiver_id`) REFERENCES `users_user` (`id`),
  CONSTRAINT `project_feedbackexchange_sender_id_a8f5bf0d_fk_users_user_id` FOREIGN KEY (`sender_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_feedbackexchange`
--

LOCK TABLES `project_feedbackexchange` WRITE;
/*!40000 ALTER TABLE `project_feedbackexchange` DISABLE KEYS */;
INSERT INTO `project_feedbackexchange` VALUES (4,'fix name and dueation','',NULL,'2025-05-25 22:03:12.630836',NULL,11,NULL,14,NULL,NULL);
/*!40000 ALTER TABLE `project_feedbackexchange` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_project`
--

DROP TABLE IF EXISTS `project_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_project` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `description` longtext,
  `academic_year` varchar(20) DEFAULT NULL,
  `team_member_count` int DEFAULT NULL,
  `field` varchar(200) DEFAULT NULL,
  `duration` int DEFAULT NULL,
  `coordinator_id` bigint DEFAULT NULL,
  `department_id` bigint DEFAULT NULL,
  `proposal_id` bigint DEFAULT NULL,
  `supervisor_id` bigint DEFAULT NULL,
  `research_file` varchar(100) DEFAULT NULL,
  `show_research_to_students` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `proposal_id` (`proposal_id`),
  KEY `project_project_coordinator_id_0d5ac125_fk_users_coo` (`coordinator_id`),
  KEY `project_project_department_id_46a52991_fk_universit` (`department_id`),
  KEY `project_project_supervisor_id_9c573892_fk_users_sup` (`supervisor_id`),
  CONSTRAINT `project_project_coordinator_id_0d5ac125_fk_users_coo` FOREIGN KEY (`coordinator_id`) REFERENCES `users_coordinator` (`user_ptr_id`),
  CONSTRAINT `project_project_department_id_46a52991_fk_universit` FOREIGN KEY (`department_id`) REFERENCES `university_department` (`id`),
  CONSTRAINT `project_project_proposal_id_1a2552be_fk_project_p` FOREIGN KEY (`proposal_id`) REFERENCES `project_projectproposal` (`id`),
  CONSTRAINT `project_project_supervisor_id_9c573892_fk_users_sup` FOREIGN KEY (`supervisor_id`) REFERENCES `users_supervisor` (`user_ptr_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_project`
--

LOCK TABLES `project_project` WRITE;
/*!40000 ALTER TABLE `project_project` DISABLE KEYS */;
INSERT INTO `project_project` VALUES (8,'proposal 1','f','2024-2025',3,'f',6,14,1,9,NULL,'',0);
/*!40000 ALTER TABLE `project_project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_projectgoal`
--

DROP TABLE IF EXISTS `project_projectgoal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_projectgoal` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `goal` longtext,
  `duration` int DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `project_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `project_projectgoal_project_id_f5e77d25_fk_project_project_id` (`project_id`),
  CONSTRAINT `project_projectgoal_project_id_f5e77d25_fk_project_project_id` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_projectgoal`
--

LOCK TABLES `project_projectgoal` WRITE;
/*!40000 ALTER TABLE `project_projectgoal` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_projectgoal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_projectlog`
--

DROP TABLE IF EXISTS `project_projectlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_projectlog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `message` longtext NOT NULL,
  `timestamp` datetime(6) NOT NULL,
  `log_type` varchar(100) DEFAULT NULL,
  `attachment` varchar(100) DEFAULT NULL,
  `project_id` bigint NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `project_projectlog_project_id_c02b4255_fk_project_project_id` (`project_id`),
  KEY `project_projectlog_user_id_45f61ba0_fk_users_user_id` (`user_id`),
  CONSTRAINT `project_projectlog_project_id_c02b4255_fk_project_project_id` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`),
  CONSTRAINT `project_projectlog_user_id_45f61ba0_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_projectlog`
--

LOCK TABLES `project_projectlog` WRITE;
/*!40000 ALTER TABLE `project_projectlog` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_projectlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_projectmembership`
--

DROP TABLE IF EXISTS `project_projectmembership`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_projectmembership` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` varchar(50) DEFAULT NULL,
  `project_id` bigint NOT NULL,
  `role_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_projectmembershi_user_id_project_id_role__47a88ed6_uniq` (`user_id`,`project_id`,`role_id`),
  KEY `project_projectmembe_project_id_266cce82_fk_project_p` (`project_id`),
  KEY `project_projectmembership_role_id_0074220b_fk_users_role_id` (`role_id`),
  CONSTRAINT `project_projectmembe_project_id_266cce82_fk_project_p` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`),
  CONSTRAINT `project_projectmembership_role_id_0074220b_fk_users_role_id` FOREIGN KEY (`role_id`) REFERENCES `users_role` (`id`),
  CONSTRAINT `project_projectmembership_user_id_77c9ac92_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_projectmembership`
--

LOCK TABLES `project_projectmembership` WRITE;
/*!40000 ALTER TABLE `project_projectmembership` DISABLE KEYS */;
INSERT INTO `project_projectmembership` VALUES (19,NULL,8,4,14),(20,NULL,8,1,4);
/*!40000 ALTER TABLE `project_projectmembership` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_projectplan`
--

DROP TABLE IF EXISTS `project_projectplan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_projectplan` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `completion_status` int DEFAULT NULL,
  `project_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_id` (`project_id`),
  CONSTRAINT `project_projectplan_project_id_eaeb574d_fk_project_project_id` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_projectplan`
--

LOCK TABLES `project_projectplan` WRITE;
/*!40000 ALTER TABLE `project_projectplan` DISABLE KEYS */;
INSERT INTO `project_projectplan` VALUES (8,NULL,8);
/*!40000 ALTER TABLE `project_projectplan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_projectproposal`
--

DROP TABLE IF EXISTS `project_projectproposal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_projectproposal` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `team_member_count` int NOT NULL,
  `field` varchar(200) NOT NULL,
  `description` longtext NOT NULL,
  `additional_comment` longtext,
  `attached_file` varchar(100) DEFAULT NULL,
  `duration` int DEFAULT NULL,
  `teacher_status` varchar(20) NOT NULL,
  `coordinator_status` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `department_id` bigint DEFAULT NULL,
  `proposed_to_id` bigint DEFAULT NULL,
  `submitted_by_id` bigint NOT NULL,
  `teacher_role_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `project_projectpropo_department_id_d162353c_fk_universit` (`department_id`),
  KEY `project_projectproposal_proposed_to_id_e4f67541_fk_users_user_id` (`proposed_to_id`),
  KEY `project_projectpropo_submitted_by_id_3e78c975_fk_users_use` (`submitted_by_id`),
  KEY `project_projectpropo_teacher_role_id_a36b5df0_fk_users_rol` (`teacher_role_id`),
  CONSTRAINT `project_projectpropo_department_id_d162353c_fk_universit` FOREIGN KEY (`department_id`) REFERENCES `university_department` (`id`),
  CONSTRAINT `project_projectpropo_submitted_by_id_3e78c975_fk_users_use` FOREIGN KEY (`submitted_by_id`) REFERENCES `users_user` (`id`),
  CONSTRAINT `project_projectpropo_teacher_role_id_a36b5df0_fk_users_rol` FOREIGN KEY (`teacher_role_id`) REFERENCES `users_role` (`id`),
  CONSTRAINT `project_projectproposal_proposed_to_id_e4f67541_fk_users_user_id` FOREIGN KEY (`proposed_to_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_projectproposal`
--

LOCK TABLES `project_projectproposal` WRITE;
/*!40000 ALTER TABLE `project_projectproposal` DISABLE KEYS */;
INSERT INTO `project_projectproposal` VALUES (9,'proposal 1',3,'f','f',NULL,'',6,'accepted','accepted','2025-05-25 20:17:14.176973','2025-05-25 20:18:51.436422',1,4,16,NULL),(11,'ruba2',3,'r','r',NULL,'',7,'pending','pending','2025-05-25 20:38:02.777790','2025-05-25 22:03:12.569434',1,4,10,NULL);
/*!40000 ALTER TABLE `project_projectproposal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_projectproposal_team_members`
--

DROP TABLE IF EXISTS `project_projectproposal_team_members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_projectproposal_team_members` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `projectproposal_id` bigint NOT NULL,
  `student_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_projectproposal__projectproposal_id_stude_e823c2db_uniq` (`projectproposal_id`,`student_id`),
  KEY `project_projectpropo_student_id_1727b16c_fk_users_stu` (`student_id`),
  CONSTRAINT `project_projectpropo_projectproposal_id_a0bb6e62_fk_project_p` FOREIGN KEY (`projectproposal_id`) REFERENCES `project_projectproposal` (`id`),
  CONSTRAINT `project_projectpropo_student_id_1727b16c_fk_users_stu` FOREIGN KEY (`student_id`) REFERENCES `users_student` (`user_ptr_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_projectproposal_team_members`
--

LOCK TABLES `project_projectproposal_team_members` WRITE;
/*!40000 ALTER TABLE `project_projectproposal_team_members` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_projectproposal_team_members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_projecttask`
--

DROP TABLE IF EXISTS `project_projecttask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_projecttask` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `outputs` longtext NOT NULL,
  `goals` longtext NOT NULL,
  `remaining_tasks` longtext NOT NULL,
  `deliverable_text` longtext,
  `deliverable_file` varchar(100) DEFAULT NULL,
  `deadline_days` int unsigned DEFAULT NULL,
  `task_status` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `assign_to_id` bigint DEFAULT NULL,
  `goal_id` bigint DEFAULT NULL,
  `project_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `project_projecttask_assign_to_id_7be346e2_fk_users_stu` (`assign_to_id`),
  KEY `project_projecttask_goal_id_c02d7d6e_fk_project_projectgoal_id` (`goal_id`),
  KEY `project_projecttask_project_id_371f4911_fk_project_project_id` (`project_id`),
  CONSTRAINT `project_projecttask_assign_to_id_7be346e2_fk_users_stu` FOREIGN KEY (`assign_to_id`) REFERENCES `users_student` (`user_ptr_id`),
  CONSTRAINT `project_projecttask_goal_id_c02d7d6e_fk_project_projectgoal_id` FOREIGN KEY (`goal_id`) REFERENCES `project_projectgoal` (`id`),
  CONSTRAINT `project_projecttask_project_id_371f4911_fk_project_project_id` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`),
  CONSTRAINT `project_projecttask_chk_1` CHECK ((`deadline_days` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_projecttask`
--

LOCK TABLES `project_projecttask` WRITE;
/*!40000 ALTER TABLE `project_projecttask` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_projecttask` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_studentprojectmembership`
--

DROP TABLE IF EXISTS `project_studentprojectmembership`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_studentprojectmembership` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` varchar(50) DEFAULT NULL,
  `project_id` bigint DEFAULT NULL,
  `proposal_id` bigint DEFAULT NULL,
  `student_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `project_studentproje_project_id_a63fd936_fk_project_p` (`project_id`),
  KEY `project_studentproje_proposal_id_bcb5539f_fk_project_p` (`proposal_id`),
  KEY `project_studentproje_student_id_2b7c1f3c_fk_users_stu` (`student_id`),
  CONSTRAINT `project_studentproje_project_id_a63fd936_fk_project_p` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`),
  CONSTRAINT `project_studentproje_proposal_id_bcb5539f_fk_project_p` FOREIGN KEY (`proposal_id`) REFERENCES `project_projectproposal` (`id`),
  CONSTRAINT `project_studentproje_student_id_2b7c1f3c_fk_users_stu` FOREIGN KEY (`student_id`) REFERENCES `users_student` (`user_ptr_id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_studentprojectmembership`
--

LOCK TABLES `project_studentprojectmembership` WRITE;
/*!40000 ALTER TABLE `project_studentprojectmembership` DISABLE KEYS */;
INSERT INTO `project_studentprojectmembership` VALUES (27,NULL,8,NULL,16),(30,NULL,NULL,11,10);
/*!40000 ALTER TABLE `project_studentprojectmembership` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `report_projectreport`
--

DROP TABLE IF EXISTS `report_projectreport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `report_projectreport` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `report_date` date NOT NULL,
  `progress` longtext,
  `work_done` longtext,
  `work_remaining` longtext,
  `challenges` longtext,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` bigint NOT NULL,
  `project_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `report_projectreport_created_by_id_776c5599_fk_users_user_id` (`created_by_id`),
  KEY `report_projectreport_project_id_1b5a0e55_fk_project_project_id` (`project_id`),
  CONSTRAINT `report_projectreport_created_by_id_776c5599_fk_users_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `users_user` (`id`),
  CONSTRAINT `report_projectreport_project_id_1b5a0e55_fk_project_project_id` FOREIGN KEY (`project_id`) REFERENCES `project_project` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `report_projectreport`
--

LOCK TABLES `report_projectreport` WRITE;
/*!40000 ALTER TABLE `report_projectreport` DISABLE KEYS */;
/*!40000 ALTER TABLE `report_projectreport` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `report_teammemberstatus`
--

DROP TABLE IF EXISTS `report_teammemberstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `report_teammemberstatus` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `status` varchar(20) NOT NULL,
  `notes` longtext,
  `report_id` bigint NOT NULL,
  `student_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `report_teammemberstatus_report_id_student_id_f00edf75_uniq` (`report_id`,`student_id`),
  KEY `report_teammembersta_student_id_e5fb7c38_fk_users_stu` (`student_id`),
  CONSTRAINT `report_teammembersta_report_id_37a6d386_fk_report_pr` FOREIGN KEY (`report_id`) REFERENCES `report_projectreport` (`id`),
  CONSTRAINT `report_teammembersta_student_id_e5fb7c38_fk_users_stu` FOREIGN KEY (`student_id`) REFERENCES `users_student` (`user_ptr_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `report_teammemberstatus`
--

LOCK TABLES `report_teammemberstatus` WRITE;
/*!40000 ALTER TABLE `report_teammemberstatus` DISABLE KEYS */;
/*!40000 ALTER TABLE `report_teammemberstatus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `university_college`
--

DROP TABLE IF EXISTS `university_college`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `university_college` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `location` varchar(200) DEFAULT NULL,
  `university_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `university_college_university_id_706875d3_fk_universit` (`university_id`),
  CONSTRAINT `university_college_university_id_706875d3_fk_universit` FOREIGN KEY (`university_id`) REFERENCES `university_university` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `university_college`
--

LOCK TABLES `university_college` WRITE;
/*!40000 ALTER TABLE `university_college` DISABLE KEYS */;
INSERT INTO `university_college` VALUES (1,'Computer Science and Information Technology',NULL,1);
/*!40000 ALTER TABLE `university_college` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `university_department`
--

DROP TABLE IF EXISTS `university_department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `university_department` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `college_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `university_departmen_college_id_93f7c54d_fk_universit` (`college_id`),
  CONSTRAINT `university_departmen_college_id_93f7c54d_fk_universit` FOREIGN KEY (`college_id`) REFERENCES `university_college` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `university_department`
--

LOCK TABLES `university_department` WRITE;
/*!40000 ALTER TABLE `university_department` DISABLE KEYS */;
INSERT INTO `university_department` VALUES (1,'Software Engineering',1),(2,'Networking',1),(3,'IT',1);
/*!40000 ALTER TABLE `university_department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `university_university`
--

DROP TABLE IF EXISTS `university_university`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `university_university` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `university_university`
--

LOCK TABLES `university_university` WRITE;
/*!40000 ALTER TABLE `university_university` DISABLE KEYS */;
INSERT INTO `university_university` VALUES (1,'Sudan University of Science and Technology');
/*!40000 ALTER TABLE `university_university` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_admin`
--

DROP TABLE IF EXISTS `users_admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_admin` (
  `user_ptr_id` bigint NOT NULL,
  PRIMARY KEY (`user_ptr_id`),
  CONSTRAINT `users_admin_user_ptr_id_4930cb66_fk_users_user_id` FOREIGN KEY (`user_ptr_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_admin`
--

LOCK TABLES `users_admin` WRITE;
/*!40000 ALTER TABLE `users_admin` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_coordinator`
--

DROP TABLE IF EXISTS `users_coordinator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_coordinator` (
  `user_ptr_id` bigint NOT NULL,
  `coord_id` varchar(20) NOT NULL,
  `is_super` tinyint(1) NOT NULL,
  PRIMARY KEY (`user_ptr_id`),
  UNIQUE KEY `coord_id` (`coord_id`),
  CONSTRAINT `users_coordinator_user_ptr_id_9ee9e14c_fk_users_user_id` FOREIGN KEY (`user_ptr_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_coordinator`
--

LOCK TABLES `users_coordinator` WRITE;
/*!40000 ALTER TABLE `users_coordinator` DISABLE KEYS */;
INSERT INTO `users_coordinator` VALUES (9,'C-9',1),(14,'C-14',0),(15,'C-15',0);
/*!40000 ALTER TABLE `users_coordinator` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_role`
--

DROP TABLE IF EXISTS `users_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_role` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_role`
--

LOCK TABLES `users_role` WRITE;
/*!40000 ALTER TABLE `users_role` DISABLE KEYS */;
INSERT INTO `users_role` VALUES (4,'Coordinator'),(3,'Judgement Committee'),(2,'Reader'),(1,'Supervisor');
/*!40000 ALTER TABLE `users_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_student`
--

DROP TABLE IF EXISTS `users_student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_student` (
  `user_ptr_id` bigint NOT NULL,
  `student_id` varchar(20) NOT NULL,
  `sitting_number` varchar(20) NOT NULL,
  PRIMARY KEY (`user_ptr_id`),
  UNIQUE KEY `student_id` (`student_id`),
  CONSTRAINT `users_student_user_ptr_id_32a2490a_fk_users_user_id` FOREIGN KEY (`user_ptr_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_student`
--

LOCK TABLES `users_student` WRITE;
/*!40000 ALTER TABLE `users_student` DISABLE KEYS */;
INSERT INTO `users_student` VALUES (10,'1','1'),(11,'201811500411','411'),(12,'201811500412','412'),(13,'201811500413','413'),(16,'201811500414','414');
/*!40000 ALTER TABLE `users_student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_supervisor`
--

DROP TABLE IF EXISTS `users_supervisor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_supervisor` (
  `user_ptr_id` bigint NOT NULL,
  `qualification` varchar(100) NOT NULL,
  `total_projects` int NOT NULL,
  `supervisor_id` varchar(20) NOT NULL,
  `work_place` varchar(100) NOT NULL,
  PRIMARY KEY (`user_ptr_id`),
  UNIQUE KEY `supervisor_id` (`supervisor_id`),
  CONSTRAINT `users_supervisor_user_ptr_id_28cfe711_fk_users_user_id` FOREIGN KEY (`user_ptr_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_supervisor`
--

LOCK TABLES `users_supervisor` WRITE;
/*!40000 ALTER TABLE `users_supervisor` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_supervisor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_user`
--

DROP TABLE IF EXISTS `users_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `phone_number` varchar(15) DEFAULT NULL,
  `department_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  KEY `users_user_department_id_626c0154_fk_university_department_id` (`department_id`),
  CONSTRAINT `users_user_department_id_626c0154_fk_university_department_id` FOREIGN KEY (`department_id`) REFERENCES `university_department` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_user`
--

LOCK TABLES `users_user` WRITE;
/*!40000 ALTER TABLE `users_user` DISABLE KEYS */;
INSERT INTO `users_user` VALUES (1,'pbkdf2_sha256$600000$3kdNaBgcsKPSKKkK8knyqO$FtcYjI91/q+fMyXcHiVa2gNCmnosD45WuYowF09GgvE=','2025-05-19 15:33:35.236074',1,'ruba','','','',1,1,'2025-05-18 17:23:46.771856',NULL,NULL),(2,'pbkdf2_sha256$600000$9u47LxQM1DDHgzHDLrrfy0$kbI10cP8Q/p3x9teumY6YEq64z9hRUX03Vnayau2qL4=','2025-05-25 22:16:46.227606',1,'admin','','','admin@example.com',1,1,'2025-05-18 17:26:27.536086',NULL,NULL),(4,'pbkdf2_sha256$600000$SRUOXWQxKsVkyz3uraSB5p$84r9/pTSQrc+EMutH4iIHDuCEarzdzQ5VnbviVsDflM=','2025-05-25 21:48:55.220569',0,'nahla','Nahla','Murtada','nahla@gmail.com',1,1,'2025-05-19 14:29:01.289447','092-114-4322',1),(5,'pbkdf2_sha256$600000$IKaQFv0t9IhCxI8FLM8GTR$/vxCqyq14Se1mtolvnTD8xQoN/37wL5ybiRAUb2c80c=','2025-05-20 22:33:34.207045',0,'hind','Hind','Alamin','hind@gmail.com',1,1,'2025-05-19 14:37:52.102890','099-634-3001',1),(6,'pbkdf2_sha256$600000$Zk0ahp2yWFM2NyGtk2VRGD$LmrDJR/PntU4vPMPtoy4cx8v0qJTa8MkjPPOF133vXU=',NULL,0,'taha','Taha','Ahmed','taha@gmail.com',1,1,'2025-05-19 14:46:32.601821','',2),(7,'pbkdf2_sha256$600000$21whbSYrQRQOUX2cPw7nVi$E7H6CO31i01sozfpfMU0nJR+CCsRy83RCTWgeLgP5KI=',NULL,0,'sami','Sami','Abdelrahman','sami@gmail.com',1,1,'2025-05-19 14:46:59.497399','',3),(9,'pbkdf2_sha256$600000$5oyaBAnzxDt1Ed5iWudlUd$dJ2hGuWTQXJhFQGUcTSs7Yo8UOKS0GqGzfjWg48cRV8=','2025-05-22 18:42:39.707030',0,'malik','Malik','Ali','',1,1,'2025-05-19 14:56:49.000000',NULL,1),(10,'pbkdf2_sha256$600000$f0HK6lrylxIBCPme3HqRBr$BubT3h2QlHvkWKOnof/rjcV5PUHj1dGI6bbhDHqKe0U=','2025-05-25 20:37:35.370663',0,'201811500410','Ruba','Salih','ruba@gmail.com',0,1,'2025-05-19 15:08:11.341786','09263974',1),(11,'pbkdf2_sha256$600000$Oo5uk80FGq93yHJ9uxC9gE$5mQWtLV3McXDety3ROerS5kedrlmIu5TvmMHRhd7PmA=','2025-05-24 22:09:22.601651',0,'201811500411','Maha','Kamal','',0,1,'2025-05-19 15:23:50.863170','',1),(12,'pbkdf2_sha256$600000$U0t5bCulxQVme9eilysm3K$ZuE+SyUtm5+evEqQQdzSLAKu2WQwiGkeG7i2CYXNbOA=','2025-05-24 22:08:53.038676',0,'201811500412','Ahmed','Omar','',0,1,'2025-05-19 15:25:21.526994','',2),(13,'pbkdf2_sha256$600000$pSdmX6Hu5cw3h1m8qRFh0k$IAoapUuU/3vEgZ1w40HxJFBt+pIzgJIV/fE5onMaYHE=','2025-05-21 18:15:16.598754',0,'201811500413','Wala','Yassin','',0,1,'2025-05-19 15:26:16.672678','',2),(14,'pbkdf2_sha256$600000$n8i4dprdHbmOPrbLZeuUly$HNS7D7HNKdfDKi0emF/DheCaQv3/CUcrKoNB8/lwv0g=','2025-05-25 22:00:51.957910',0,'fadwa','Fadwa','Abd Alazim Ahmed','',0,1,'2025-05-19 15:27:20.170652','',1),(15,'pbkdf2_sha256$600000$CBkLDWbeRgAGgEOusQHgBZ$buSslcKbcE+Vbzym0MSR2Ri3HUJnOPoYoEC2UV/Vh6s=',NULL,0,'dan','Dan','Mahmoud','',0,1,'2025-05-19 15:40:41.529143','',2),(16,'pbkdf2_sha256$600000$c8c66V3EDEjE5BuZR3G2Lc$eUbUnHOvzqwWMz2bnIZr52dMoJozuhRsJHdll6u1Cdk=','2025-05-25 20:16:42.004343',0,'201811500414','Amin','Yassin','',0,1,'2025-05-19 15:42:47.915584','',1);
/*!40000 ALTER TABLE `users_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_user_groups`
--

DROP TABLE IF EXISTS `users_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_user_groups_user_id_group_id_b88eab82_uniq` (`user_id`,`group_id`),
  KEY `users_user_groups_group_id_9afc8d0e_fk_auth_group_id` (`group_id`),
  CONSTRAINT `users_user_groups_group_id_9afc8d0e_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `users_user_groups_user_id_5f6f5a90_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_user_groups`
--

LOCK TABLES `users_user_groups` WRITE;
/*!40000 ALTER TABLE `users_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_user_user_permissions`
--

DROP TABLE IF EXISTS `users_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_user_user_permissions_user_id_permission_id_43338c45_uniq` (`user_id`,`permission_id`),
  KEY `users_user_user_perm_permission_id_0b93982e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `users_user_user_perm_permission_id_0b93982e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `users_user_user_permissions_user_id_20aca447_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_user_user_permissions`
--

LOCK TABLES `users_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `users_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_usercreationlog`
--

DROP TABLE IF EXISTS `users_usercreationlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_usercreationlog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `added_at` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  `added_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `users_usercreationlo_added_by_id_8e9288a2_fk_users_coo` (`added_by_id`),
  CONSTRAINT `users_usercreationlo_added_by_id_8e9288a2_fk_users_coo` FOREIGN KEY (`added_by_id`) REFERENCES `users_coordinator` (`user_ptr_id`),
  CONSTRAINT `users_usercreationlog_user_id_dfa67f0b_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_usercreationlog`
--

LOCK TABLES `users_usercreationlog` WRITE;
/*!40000 ALTER TABLE `users_usercreationlog` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_usercreationlog` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-26  1:39:54
