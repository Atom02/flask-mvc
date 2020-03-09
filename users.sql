/*
 Navicat Premium Data Transfer

 Source Server         : SANTANU_PUBLIC
 Source Server Type    : MariaDB
 Source Server Version : 100225
 Source Host           : 192.168.3.19:3306
 Source Schema         : santanu

 Target Server Type    : MariaDB
 Target Server Version : 100225
 File Encoding         : 65001

 Date: 02/03/2020 12:07:27
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_name` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `name` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `auth_key` text CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `password_hash` text CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `password_reset_token` text CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `email` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `created_at` timestamp(0) NULL DEFAULT NULL,
  `updated_at` timestamp(0) NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP(0),
  `status` smallint(6) NULL DEFAULT 1,
  `created_by` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  PRIMARY KEY (`user_id`) USING BTREE,
  UNIQUE INDEX `user_name`(`user_name`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
