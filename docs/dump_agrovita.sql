-- MySQL dump 10.13  Distrib 8.4.13, for Win64 (x86_64)
--
-- Host: localhost    Database: agrovita
-- ------------------------------------------------------
-- Server version	8.4.13

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
-- Current Database: `agrovita`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `agrovita` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `agrovita`;

--
-- Table structure for table `animais`
--

DROP TABLE IF EXISTS `animais`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `animais` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `identificacao` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `especie` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `raca` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `data_nascimento` date DEFAULT NULL,
  `usuario_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_animais_usuario` (`usuario_id`),
  CONSTRAINT `fk_animais_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `animais`
--

LOCK TABLES `animais` WRITE;
/*!40000 ALTER TABLE `animais` DISABLE KEYS */;
INSERT INTO `animais` VALUES (9,'BOV-001','Bovino','Angus','2024-03-12',2),(10,'BOV-002','Bovino','Nelore','2023-06-20',1),(11,'BOV-003','Bovino','Gir','2025-02-10',1);
/*!40000 ALTER TABLE `animais` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logs_auditoria`
--

DROP TABLE IF EXISTS `logs_auditoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `logs_auditoria` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `usuario_id` bigint DEFAULT NULL,
  `acao` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `detalhes` text COLLATE utf8mb4_unicode_ci,
  `data_hora` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_logs_usuario` (`usuario_id`),
  CONSTRAINT `fk_logs_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=68 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logs_auditoria`
--

LOCK TABLES `logs_auditoria` WRITE;
/*!40000 ALTER TABLE `logs_auditoria` DISABLE KEYS */;
INSERT INTO `logs_auditoria` VALUES (1,1,'LOGOUT','Logout realizado pelo usuário','2026-10-09 19:42:28'),(2,1,'LOGIN','Login realizado com sucesso','2026-10-09 19:42:59'),(3,1,'CRIAR_ANIMAL','Animal ID 10 cadastrado','2026-10-09 19:48:31'),(4,1,'EXCLUIR_ANIMAL','Animal ID 6 excluído','2026-10-09 19:51:49'),(5,1,'EDITAR_ANIMAL','Animal ID 10 atualizado','2026-10-09 19:51:55'),(6,1,'CRIAR_MANEJO','Manejo ID 5 cadastrado','2026-10-09 19:55:03'),(7,1,'EXCLUIR_MANEJO','Manejo ID 3 excluído','2026-10-09 19:55:12'),(8,1,'EDITAR_MANEJO','Manejo ID 5 atualizado','2026-10-09 19:55:20'),(9,1,'EDITAR_VACINACAO','Vacinação ID 3 atualizada','2026-10-09 20:02:50'),(10,1,'EXCLUIR_VACINACAO','Vacinação ID 3 excluída','2026-10-09 20:02:55'),(11,1,'CRIAR_VACINACAO','Vacinação ID 5 cadastrada','2026-10-09 20:03:18'),(12,1,'LOGOUT','Logout realizado pelo usuário','2026-10-09 20:07:07'),(13,2,'LOGIN','Login realizado com sucesso','2026-10-09 20:07:15'),(14,2,'ACESSO_NEGADO','Tentativa de acesso a uma área administrativa','2026-10-09 20:07:44'),(15,2,'SESSAO_EXPIRADA','Sessão encerrada após 30 minutos de inatividade','2026-10-09 20:09:36'),(16,2,'LOGIN','Login realizado com sucesso','2026-10-09 20:09:52'),(17,2,'SESSAO_EXPIRADA','Sessão encerrada após 30 minutos de inatividade','2026-10-09 20:10:12'),(18,2,'LOGIN','Login realizado com sucesso','2026-10-09 20:38:16'),(19,2,'LOGOUT','Logout realizado pelo usuário','2026-10-09 20:38:28'),(20,2,'LOGIN','Login realizado com sucesso','2026-10-09 20:39:45'),(21,2,'LOGOUT','Logout realizado pelo usuário','2026-10-09 20:39:55'),(22,1,'LOGIN','Login realizado com sucesso','2026-10-10 16:43:49'),(23,1,'CRIAR_ANIMAIS','Registro ID 11 criado pela API','2026-10-10 17:05:12'),(24,1,'ATUALIZAR_ANIMAIS','Registro ID 11 atualizado pela API','2026-10-10 17:10:43'),(25,1,'ATUALIZAR_ANIMAIS','Registro ID 11 atualizado pela API','2026-10-10 17:13:37'),(26,1,'EXCLUIR_ANIMAIS','Registro ID 11 excluído pela API','2026-10-10 17:14:48'),(27,1,'CRIAR_MANEJOS','Registro ID 6 criado pela API','2026-10-10 17:34:30'),(28,1,'ATUALIZAR_MANEJOS','Registro ID 6 atualizado pela API','2026-10-10 17:50:10'),(29,1,'EXCLUIR_MANEJOS','Registro ID 6 excluído pela API','2026-10-10 17:50:47'),(30,1,'CRIAR_VACINACOES','Registro ID 6 criado pela API','2026-10-10 17:52:00'),(31,1,'ATUALIZAR_VACINACOES','Registro ID 6 atualizado pela API','2026-10-10 17:55:19'),(32,1,'EXCLUIR_VACINACOES','Registro ID 6 excluído pela API','2026-10-10 17:56:28'),(33,1,'LOGIN','Login realizado com sucesso','2026-10-10 20:02:53'),(34,NULL,'LOGOUT','Logout realizado pelo usuário','2026-10-10 21:08:12'),(35,1,'LOGIN','Login realizado com sucesso','2026-10-10 21:09:25'),(36,1,'LOGOUT','Logout realizado pelo usuário','2026-10-10 21:31:16'),(37,NULL,'LOGIN','Login realizado com sucesso','2026-10-10 21:31:27'),(38,NULL,'ACESSO_NEGADO','Tentativa de acesso a uma área administrativa','2026-10-10 21:31:35'),(39,NULL,'LOGOUT','Logout realizado pelo usuário','2026-10-10 21:31:40'),(40,1,'LOGIN','Login realizado com sucesso','2026-10-10 21:38:20'),(41,1,'CRIAR_VACINACAO','Vacinação ID 7 cadastrada','2026-10-10 21:47:38'),(42,1,'LOGIN','Login realizado com sucesso','2026-10-21 20:50:43'),(43,1,'LOGOUT','Logout realizado pelo usuário','2026-10-21 20:53:01'),(44,NULL,'LOGOUT','Logout realizado pelo usuário','2026-10-21 20:53:20'),(45,NULL,'LOGOUT','Logout realizado pelo usuário','2026-10-21 20:53:36'),(46,1,'LOGIN','Login realizado com sucesso','2026-10-21 20:53:48'),(47,1,'CRIAR_ANIMAL','Animal ID 11 cadastrado','2026-10-21 20:54:09'),(48,1,'EDITAR_ANIMAL','Animal ID 10 atualizado','2026-10-21 20:54:35'),(49,1,'CRIAR_VACINACAO','Vacinação ID 8 cadastrada','2026-10-21 21:01:05'),(50,1,'CRIAR_MANEJO','Manejo ID 1 cadastrado','2026-10-21 21:02:33'),(51,1,'EDITAR_MANEJO','Manejo ID 1 atualizado','2026-10-21 21:04:02'),(52,1,'EXCLUIR_MANEJO','Manejo ID 1 excluído','2026-10-21 21:04:08'),(53,1,'EDITAR_VACINACAO','Vacinação ID 8 atualizada','2026-10-21 21:04:52'),(54,1,'EXCLUIR_VACINACAO','Vacinação ID 8 excluída','2026-10-21 21:05:10'),(55,1,'CRIAR_ANIMAIS','Registro ID 12 criado pela API','2026-10-21 21:10:50'),(56,1,'ATUALIZAR_ANIMAIS','Registro ID 12 atualizado pela API','2026-10-21 21:11:45'),(57,1,'EXCLUIR_ANIMAIS','Registro ID 12 excluído pela API','2026-10-21 21:12:24'),(58,1,'LOGOUT','Logout realizado pelo usuário','2026-10-21 21:39:22'),(59,2,'LOGIN','Login realizado com sucesso','2026-10-21 21:39:31'),(60,2,'LOGOUT','Logout realizado pelo usuário','2026-10-21 21:53:47'),(61,1,'LOGIN','Login realizado com sucesso','2026-10-21 21:54:03'),(62,1,'LOGIN','Login realizado com sucesso','2026-10-24 18:18:34'),(63,1,'LOGOUT','Logout realizado pelo usuário','2026-10-24 18:19:57'),(64,NULL,'LOGOUT','Logout realizado pelo usuário','2026-10-24 18:20:12'),(65,2,'LOGIN','Login realizado com sucesso','2026-10-24 18:20:23'),(66,2,'ACESSO_NEGADO','Tentativa de acesso a uma área administrativa','2026-10-24 18:21:37'),(67,2,'LOGOUT','Logout realizado pelo usuário','2026-10-24 18:31:14');
/*!40000 ALTER TABLE `logs_auditoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `manejos`
--

DROP TABLE IF EXISTS `manejos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `manejos` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `animal_id` bigint NOT NULL,
  `usuario_id` bigint NOT NULL,
  `tipo_manejo` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `data_manejo` date NOT NULL,
  `produto` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dose` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `responsavel` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `observacoes` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `fk_manejos_animal` (`animal_id`),
  KEY `fk_manejos_usuario` (`usuario_id`),
  CONSTRAINT `fk_manejos_animal` FOREIGN KEY (`animal_id`) REFERENCES `animais` (`id`),
  CONSTRAINT `fk_manejos_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `manejos`
--

LOCK TABLES `manejos` WRITE;
/*!40000 ALTER TABLE `manejos` DISABLE KEYS */;
/*!40000 ALTER TABLE `manejos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `senha` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tipo` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'usuario',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'Administrador','admin@agrovita.com','scrypt:32768:8:1$OPPGDk0Xn0ZClZPe$8b85f13e169e41080674bf4840edd5ac2eee8a4f0a9c33b1885e9a84f89a7813e029a66aa714e283df29784baeae82e73ed48ed34542c6cbd689e865ff8d954a','admin'),(2,'Usuário Teste','usuario@agrovita.com','scrypt:32768:8:1$gBkLeu3w5xsAMIXl$c4c6ebf2f3b1e35d8440ccf9da31a3b81ff1ed8be7bec54204f160f85a3153a302d8aefa0e5d0039ac35666aa37295bcb2d0d570735791698c7c2068c3837d3d','usuario');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vacinacoes`
--

DROP TABLE IF EXISTS `vacinacoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vacinacoes` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `animal_id` bigint NOT NULL,
  `usuario_id` bigint NOT NULL,
  `vacina` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `lote` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fabricante` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `data_aplicacao` date NOT NULL,
  `proxima_dose` date DEFAULT NULL,
  `dose` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `responsavel` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `observacoes` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `fk_vacinacoes_animal` (`animal_id`),
  KEY `fk_vacinacoes_usuario` (`usuario_id`),
  CONSTRAINT `fk_vacinacoes_animal` FOREIGN KEY (`animal_id`) REFERENCES `animais` (`id`),
  CONSTRAINT `fk_vacinacoes_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vacinacoes`
--

LOCK TABLES `vacinacoes` WRITE;
/*!40000 ALTER TABLE `vacinacoes` DISABLE KEYS */;
INSERT INTO `vacinacoes` VALUES (5,10,1,'raiva','RAI-2026-001','Fabricante Exemplo','2026-10-08','2026-10-12','5ml','Responsável técnico',''),(7,10,1,'febre_aftosa','VAC-2026-002','Fabricante Exemplo','2026-10-07','2026-10-28','','Responsável técnico','');
/*!40000 ALTER TABLE `vacinacoes` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50003 TRIGGER `trg_validar_datas_vacinacao_insert` BEFORE INSERT ON `vacinacoes` FOR EACH ROW BEGIN
    IF NEW.proxima_dose IS NOT NULL
        AND NEW.proxima_dose < NEW.data_aplicacao THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT =
                'A proxima dose nao pode ser anterior a data de aplicacao.';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50003 TRIGGER `trg_validar_datas_vacinacao_update` BEFORE UPDATE ON `vacinacoes` FOR EACH ROW BEGIN
    IF NEW.proxima_dose IS NOT NULL
        AND NEW.proxima_dose < NEW.data_aplicacao THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT =
                'A proxima dose nao pode ser anterior a data de aplicacao.';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Dumping routines for database 'agrovita'
--
/*!50003 DROP FUNCTION IF EXISTS `fn_total_vacinacoes_animal` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE FUNCTION `fn_total_vacinacoes_animal`(
    p_animal_id BIGINT
) RETURNS bigint
    READS SQL DATA
BEGIN
    DECLARE v_total BIGINT DEFAULT 0;

    SELECT COUNT(*)
    INTO v_total
    FROM vacinacoes
    WHERE animal_id = p_animal_id;

    RETURN v_total;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_historico_vacinacoes` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE PROCEDURE `sp_historico_vacinacoes`(
    IN p_animal_id BIGINT
)
    READS SQL DATA
BEGIN
    SELECT
        id,
        animal_id,
        vacina,
        lote,
        fabricante,
        data_aplicacao,
        proxima_dose,
        dose,
        responsavel,
        observacoes
    FROM vacinacoes
    WHERE animal_id = p_animal_id
    ORDER BY data_aplicacao DESC, id DESC;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-25 16:46:55
