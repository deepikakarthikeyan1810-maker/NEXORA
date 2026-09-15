-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: sih_project
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alerts`
--

DROP TABLE IF EXISTS `alerts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alerts` (
  `alert_id` int NOT NULL AUTO_INCREMENT,
  `call_id` int DEFAULT NULL,
  `alert_message` varchar(255) DEFAULT NULL,
  `alert_time` datetime DEFAULT NULL,
  `alert_status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`alert_id`),
  KEY `call_id` (`call_id`),
  CONSTRAINT `alerts_ibfk_1` FOREIGN KEY (`call_id`) REFERENCES `calls` (`call_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alerts`
--

LOCK TABLES `alerts` WRITE;
/*!40000 ALTER TABLE `alerts` DISABLE KEYS */;
INSERT INTO `alerts` VALUES (1,1,'Warning: Possible voice cloning detected!','2026-09-12 19:18:35','New');
/*!40000 ALTER TABLE `alerts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_logs` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `event_type` varchar(50) DEFAULT NULL,
  `event_description` varchar(255) DEFAULT NULL,
  `log_time` datetime DEFAULT NULL,
  PRIMARY KEY (`log_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `audit_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_logs`
--

LOCK TABLES `audit_logs` WRITE;
/*!40000 ALTER TABLE `audit_logs` DISABLE KEYS */;
INSERT INTO `audit_logs` VALUES (1,1,'LOGIN_SUCCESS','User logged in successfully','2026-09-13 13:16:39'),(2,1,'HIGH_RISK_CALL','High-risk voice cloning detected','2026-09-13 13:16:39'),(3,1,'ALERT_GENERATED','Security alert generated for the call','2026-09-13 13:16:39');
/*!40000 ALTER TABLE `audit_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `calls`
--

DROP TABLE IF EXISTS `calls`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `calls` (
  `call_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `call_time` datetime DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`call_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `calls_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `calls`
--

LOCK TABLES `calls` WRITE;
/*!40000 ALTER TABLE `calls` DISABLE KEYS */;
INSERT INTO `calls` VALUES (1,1,'2026-09-12 19:13:11','Analyzing');
/*!40000 ALTER TABLE `calls` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Arun','arun@gmail.com','Arun@123');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `voice_analysis`
--

DROP TABLE IF EXISTS `voice_analysis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voice_analysis` (
  `analysis_id` int NOT NULL AUTO_INCREMENT,
  `call_id` int DEFAULT NULL,
  `language` varchar(50) DEFAULT NULL,
  `voice_score` decimal(5,2) DEFAULT NULL,
  `risk_score` decimal(5,2) DEFAULT NULL,
  `result` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`analysis_id`),
  KEY `call_id` (`call_id`),
  CONSTRAINT `voice_analysis_ibfk_1` FOREIGN KEY (`call_id`) REFERENCES `calls` (`call_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `voice_analysis`
--

LOCK TABLES `voice_analysis` WRITE;
/*!40000 ALTER TABLE `voice_analysis` DISABLE KEYS */;
INSERT INTO `voice_analysis` VALUES (1,1,'English',42.50,85.00,'High Risk');
/*!40000 ALTER TABLE `voice_analysis` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-15 10:07:55
