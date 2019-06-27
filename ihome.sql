-- MySQL dump 10.13  Distrib 5.7.26, for Linux (x86_64)
--
-- Host: localhost    Database: ihome
-- ------------------------------------------------------
-- Server version	5.7.26-0ubuntu0.18.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('27a82a16dc40');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ihome_area`
--

DROP TABLE IF EXISTS `ihome_area`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ihome_area` (
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ihome_area`
--

LOCK TABLES `ihome_area` WRITE;
/*!40000 ALTER TABLE `ihome_area` DISABLE KEYS */;
INSERT INTO `ihome_area` VALUES (NULL,NULL,1,'锦江区'),(NULL,NULL,2,'青羊区'),(NULL,NULL,3,'金牛区'),(NULL,NULL,4,'武侯区'),(NULL,NULL,5,'成华区'),(NULL,NULL,6,'龙泉驿区'),(NULL,NULL,7,'青白江区'),(NULL,NULL,8,'新都区'),(NULL,NULL,9,'温江区'),(NULL,NULL,10,'郫都区'),(NULL,NULL,11,'双流区'),(NULL,NULL,12,'高新区'),(NULL,NULL,13,'天府新区'),(NULL,NULL,14,'新津县'),(NULL,NULL,15,'大邑县'),(NULL,NULL,16,'金堂县');
/*!40000 ALTER TABLE `ihome_area` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ihome_facility`
--

DROP TABLE IF EXISTS `ihome_facility`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ihome_facility` (
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `css` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ihome_facility`
--

LOCK TABLES `ihome_facility` WRITE;
/*!40000 ALTER TABLE `ihome_facility` DISABLE KEYS */;
INSERT INTO `ihome_facility` VALUES (NULL,NULL,1,'无线网络',NULL),(NULL,NULL,2,'热水淋浴',NULL),(NULL,NULL,3,'空调',NULL),(NULL,NULL,4,'暖气',NULL),(NULL,NULL,5,'允许吸烟',NULL),(NULL,NULL,6,'饮水设备',NULL),(NULL,NULL,7,'牙具',NULL),(NULL,NULL,8,'香皂',NULL),(NULL,NULL,9,'拖鞋',NULL),(NULL,NULL,10,'手纸',NULL),(NULL,NULL,11,'毛巾',NULL),(NULL,NULL,12,'沐浴露、洗发露',NULL),(NULL,NULL,13,'冰箱',NULL),(NULL,NULL,14,'洗衣机',NULL),(NULL,NULL,15,'电梯',NULL),(NULL,NULL,16,'允许做饭',NULL),(NULL,NULL,17,'允许带宠物',NULL),(NULL,NULL,18,'允许聚会',NULL),(NULL,NULL,19,'门禁系统',NULL),(NULL,NULL,20,'停车位',NULL),(NULL,NULL,21,'有线网络',NULL),(NULL,NULL,22,'电视',NULL),(NULL,NULL,23,'浴缸',NULL);
/*!40000 ALTER TABLE `ihome_facility` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ihome_house`
--

DROP TABLE IF EXISTS `ihome_house`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ihome_house` (
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `area_id` int(11) NOT NULL,
  `title` varchar(64) NOT NULL,
  `price` int(11) DEFAULT NULL,
  `address` varchar(512) DEFAULT NULL,
  `room_count` int(11) DEFAULT NULL,
  `acreage` int(11) DEFAULT NULL,
  `unit` varchar(32) DEFAULT NULL,
  `capacity` int(11) DEFAULT NULL,
  `beds` varchar(64) DEFAULT NULL,
  `deposit` int(11) DEFAULT NULL,
  `min_days` int(11) DEFAULT NULL,
  `max_days` int(11) DEFAULT NULL,
  `order_count` int(11) DEFAULT NULL,
  `index_image_url` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `area_id` (`area_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `ihome_house_ibfk_1` FOREIGN KEY (`area_id`) REFERENCES `ihome_area` (`id`),
  CONSTRAINT `ihome_house_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `ihome_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ihome_house`
--

LOCK TABLES `ihome_house` WRITE;
/*!40000 ALTER TABLE `ihome_house` DISABLE KEYS */;
INSERT INTO `ihome_house` VALUES ('2019-06-24 20:08:14','2019-06-24 20:08:14',1,1,1,'中央公馆1号',15000,'Wen two road, West Lake international science and technology building B3-1011',1,40,'一室一厅',1,'双人床1.8',30000,1,0,0,''),('2019-06-24 20:42:25','2019-06-24 20:42:25',2,1,1,'中央公馆2号',15000,'Wen two road, West Lake international science and technology building B3-1011',1,40,'一室一厅',1,'双人床1.8',30000,1,0,0,''),('2019-06-24 23:10:16','2019-06-24 23:21:21',3,1,1,'中央公馆3号',20000,'Wen two road, West Lake international science and technology building B3-1011',1,60,'二室一厅',3,'双人床1.8',50000,1,0,0,'20190624232137.jpg'),('2019-06-24 23:49:14','2019-06-24 23:49:14',4,1,2,'中央公馆4号',15000,'Wen two road, West Lake international science and technology building B3-1011',1,40,'一室一厅',2,'双人床1.8',30000,1,0,0,'/static/upload/20190624235836.jpg'),('2019-06-25 01:32:03','2019-06-25 01:32:03',5,1,1,'西湖1号',20000,'哈利了哈路135号',1,40,'一室一厅',2,'双人床1.8',30000,1,0,0,'/static/upload/20190625013620.jpg'),('2019-06-25 01:32:03','2019-06-25 01:32:03',6,1,1,'西湖2号',20000,'哈哈哈啊撸路125号',1,40,'一室一厅',1,'双人床1.8',30000,1,0,0,'/static/upload/20190625014153.jpg'),('2019-06-25 19:03:51','2019-06-25 19:03:51',7,1,1,'西湖3号',25000,'Wen two road, West Lake international science and technology building B3-1011',1,40,'二室一厅',3,'双人床1.8',30000,1,0,0,'/static/upload/20190625190719.jpg'),('2019-06-25 19:03:51','2019-06-25 19:03:51',8,1,1,'西湖4号',30000,'Wen two road, West Lake international science and technology building B3-1011',1,60,'二室一厅',4,'双人床1.8',50000,1,0,0,'/static/upload/20190625190842.jpg'),('2019-06-25 19:03:51','2019-06-26 21:18:51',9,1,1,'西湖5号',23000,'Wen two road, West Lake international science and technology building B3-1011',1,40,'一室一厅',2,'双人床1.8',30000,1,0,1,'/static/upload/20190625191024.jpg');
/*!40000 ALTER TABLE `ihome_house` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ihome_house_facility`
--

DROP TABLE IF EXISTS `ihome_house_facility`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ihome_house_facility` (
  `house_id` int(11) NOT NULL,
  `facility_id` int(11) NOT NULL,
  PRIMARY KEY (`house_id`,`facility_id`),
  KEY `facility_id` (`facility_id`),
  CONSTRAINT `ihome_house_facility_ibfk_1` FOREIGN KEY (`facility_id`) REFERENCES `ihome_facility` (`id`),
  CONSTRAINT `ihome_house_facility_ibfk_2` FOREIGN KEY (`house_id`) REFERENCES `ihome_house` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ihome_house_facility`
--

LOCK TABLES `ihome_house_facility` WRITE;
/*!40000 ALTER TABLE `ihome_house_facility` DISABLE KEYS */;
INSERT INTO `ihome_house_facility` VALUES (1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(1,3),(2,3),(3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(9,3),(2,4),(5,4),(6,4),(9,4),(1,6),(5,6),(7,6),(5,8),(5,10),(6,10),(5,12),(7,12),(8,12),(9,12),(1,13),(2,13),(3,13),(4,13),(5,13),(6,13),(7,13),(8,13),(9,13),(1,14),(2,14),(3,14),(4,14),(5,14),(6,14),(7,14),(8,14),(9,14),(1,15),(2,15),(3,15),(4,15),(5,15),(6,15),(7,15),(8,15),(9,15),(8,16),(2,19),(3,19),(7,19),(8,20),(7,21),(1,22),(2,22),(3,22),(4,22),(5,22),(6,22),(7,22),(8,22),(9,22),(1,23),(4,23),(5,23),(6,23),(7,23),(8,23),(9,23);
/*!40000 ALTER TABLE `ihome_house_facility` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ihome_house_image`
--

DROP TABLE IF EXISTS `ihome_house_image`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ihome_house_image` (
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `house_id` int(11) NOT NULL,
  `url` varchar(256) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `house_id` (`house_id`),
  CONSTRAINT `ihome_house_image_ibfk_1` FOREIGN KEY (`house_id`) REFERENCES `ihome_house` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ihome_house_image`
--

LOCK TABLES `ihome_house_image` WRITE;
/*!40000 ALTER TABLE `ihome_house_image` DISABLE KEYS */;
INSERT INTO `ihome_house_image` VALUES ('2019-06-24 23:21:21','2019-06-24 23:21:21',1,3,'20190624232137.jpg'),('2019-06-24 23:31:21','2019-06-24 23:31:21',2,3,'20190624233126.jpg'),('2019-06-24 23:36:09','2019-06-24 23:36:09',3,3,'/static/upload/20190624233615.jpg'),('2019-06-24 23:36:09','2019-06-24 23:36:09',4,3,'/static/upload/20190624233625.jpg'),('2019-06-24 23:49:14','2019-06-24 23:49:14',5,4,'/static/upload/20190624235836.jpg'),('2019-06-24 23:49:14','2019-06-24 23:49:14',6,4,'/static/upload/20190624235841.jpg'),('2019-06-24 23:49:14','2019-06-24 23:49:14',7,4,'/static/upload/20190624235847.jpg'),('2019-06-25 01:32:03','2019-06-25 01:32:03',8,5,'/static/upload/20190625013620.jpg'),('2019-06-25 01:32:03','2019-06-25 01:32:03',9,5,'/static/upload/20190625013627.jpg'),('2019-06-25 01:32:03','2019-06-25 01:32:03',10,5,'/static/upload/20190625013633.jpg'),('2019-06-25 01:32:03','2019-06-25 01:32:03',11,6,'/static/upload/20190625014153.jpg'),('2019-06-25 01:32:03','2019-06-25 01:32:03',12,6,'/static/upload/20190625014157.jpg'),('2019-06-25 01:32:03','2019-06-25 01:32:03',13,6,'/static/upload/20190625014200.jpg'),('2019-06-25 19:03:51','2019-06-25 19:03:51',14,7,'/static/upload/20190625190719.jpg'),('2019-06-25 19:03:51','2019-06-25 19:03:51',15,7,'/static/upload/20190625190727.jpg'),('2019-06-25 19:03:51','2019-06-25 19:03:51',16,7,'/static/upload/20190625190737.jpg'),('2019-06-25 19:03:51','2019-06-25 19:03:51',17,8,'/static/upload/20190625190842.jpg'),('2019-06-25 19:03:51','2019-06-25 19:03:51',18,8,'/static/upload/20190625190851.jpg'),('2019-06-25 19:03:51','2019-06-25 19:03:51',19,8,'/static/upload/20190625190859.jpg'),('2019-06-25 19:03:51','2019-06-25 19:03:51',20,9,'/static/upload/20190625191024.jpg'),('2019-06-25 19:03:51','2019-06-25 19:03:51',21,9,'/static/upload/20190625191031.jpg'),('2019-06-25 19:03:51','2019-06-25 19:03:51',22,9,'/static/upload/20190625191036.jpg');
/*!40000 ALTER TABLE `ihome_house_image` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ihome_order`
--

DROP TABLE IF EXISTS `ihome_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ihome_order` (
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `house_id` int(11) NOT NULL,
  `begin_date` datetime NOT NULL,
  `end_date` datetime NOT NULL,
  `days` int(11) NOT NULL,
  `house_price` int(11) NOT NULL,
  `amount` int(11) NOT NULL,
  `status` enum('WAIT_ACCEPT','WAIT_PAYMENT','PAID','WAIT_COMMENT','COMPLETE','CANCELED','REJECTED') DEFAULT NULL,
  `comment` text,
  `trade_no` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `house_id` (`house_id`),
  KEY `user_id` (`user_id`),
  KEY `ix_ihome_order_status` (`status`),
  CONSTRAINT `ihome_order_ibfk_1` FOREIGN KEY (`house_id`) REFERENCES `ihome_house` (`id`),
  CONSTRAINT `ihome_order_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `ihome_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ihome_order`
--

LOCK TABLES `ihome_order` WRITE;
/*!40000 ALTER TABLE `ihome_order` DISABLE KEYS */;
INSERT INTO `ihome_order` VALUES ('2019-06-25 23:28:19','2019-06-26 21:18:51',1,2,9,'2019-06-26 00:00:00','2019-06-27 00:00:00',2,23000,46000,'COMPLETE','这房间不错',NULL),('2019-06-26 00:40:04','2019-06-26 00:40:04',2,3,9,'2019-06-28 00:00:00','2019-06-28 00:00:00',1,23000,23000,'REJECTED','房间清理装修，需要一周时间',NULL);
/*!40000 ALTER TABLE `ihome_order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ihome_user`
--

DROP TABLE IF EXISTS `ihome_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ihome_user` (
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(11) DEFAULT NULL,
  `name` varchar(30) DEFAULT NULL,
  `avatar_url` varchar(100) DEFAULT NULL,
  `real_id_card` varchar(18) DEFAULT NULL,
  `real_name` varchar(30) DEFAULT NULL,
  `pwd_hash` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `phone` (`phone`),
  UNIQUE KEY `real_id_card` (`real_id_card`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ihome_user`
--

LOCK TABLES `ihome_user` WRITE;
/*!40000 ALTER TABLE `ihome_user` DISABLE KEYS */;
INSERT INTO `ihome_user` VALUES ('2019-06-21 01:30:26','2019-06-24 01:26:54',1,'13516804560','何足道',NULL,'666111122233331234','何足道','pbkdf2:sha256:150000$z4ImHN5C$e4019fef38020a7960da2c8ee1920e3895a88a3438613c3bab4831ff682c810b'),('2019-06-25 22:50:53','2019-06-25 22:50:53',2,'13511111111','13511111111',NULL,NULL,NULL,'pbkdf2:sha256:150000$manN46zn$02ee83fe47799bd92486242a117044087596ff542288f5b383e90b5c9cb42a9d'),('2019-06-26 00:40:04','2019-06-26 00:40:04',3,'13522222222','13522222222',NULL,NULL,NULL,'pbkdf2:sha256:150000$HKsgygDI$91334e4f28b9a137a998230b3ab2f1c623b7592726a985293e36dc1e7a639200');
/*!40000 ALTER TABLE `ihome_user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-06-27  1:11:48
