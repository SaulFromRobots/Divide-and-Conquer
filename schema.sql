-- schema.sql, version 1

-- Design changes come in version 2.
-- Run it on an empty database:
--   mysql -u dac -p dac_dev < schema.sql
-- The app checks the version in this table when it starts.
CREATE TABLE `InstanceGlobals` (
  `SchemaVersion` int NOT NULL,
  `ContactEmail` mediumtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Users` (
  `ID` int unsigned NOT NULL AUTO_INCREMENT,
  `Name` varchar(256) NOT NULL,
  `Email` mediumtext NOT NULL,
  `HashedPass` mediumtext NOT NULL,
  `Color` varchar(6) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ID_UNIQUE` (`ID`),
  UNIQUE KEY `Name_UNIQUE` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Sessions has a foreign key to Users, so it comes after Users.
CREATE TABLE `Sessions` (
  `ID` int unsigned NOT NULL AUTO_INCREMENT,
  `UserID` int unsigned NOT NULL,
  `Token` varchar(256) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `LastUsed` timestamp NOT NULL,
  PRIMARY KEY (`ID`,`UserID`),
  UNIQUE KEY `ID_UNIQUE` (`ID`),
  UNIQUE KEY `Token_UNIQUE` (`Token`),
  KEY `UserID_INDEX` (`UserID`),
  CONSTRAINT `fk_sessions_user` FOREIGN KEY (`UserID`) REFERENCES `Users` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `Lists` (
  `ID` int unsigned NOT NULL AUTO_INCREMENT,
  `Name` mediumtext NOT NULL,
  `Owners` mediumtext NOT NULL,
  `Collaborators` mediumtext NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ID_UNIQUE` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Items has a foreign key to Lists, so it comes after Lists.
CREATE TABLE `Items` (
  `ID` int unsigned NOT NULL AUTO_INCREMENT,
  `ListID` int unsigned NOT NULL,
  `Text` mediumtext NOT NULL,
  `Assignee` int NOT NULL,
  `State` enum('No progress','In progress','Done') NOT NULL,
  `OrderPlacement` int NOT NULL,
  PRIMARY KEY (`ID`,`ListID`),
  UNIQUE KEY `ID_UNIQUE` (`ID`),
  UNIQUE KEY `ListID_UNIQUE` (`ListID`),
  CONSTRAINT `ID` FOREIGN KEY (`ListID`) REFERENCES `Lists` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `MembershipChanges` (
  `ID` int unsigned NOT NULL AUTO_INCREMENT,
  `ListID` int NOT NULL,
  `UserID` int NOT NULL,
  `NewMemberType` enum('Colab','Owner') NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ID_UNIQUE` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- SchemaVersion must match SCHEMA_VERSION in db.py.
INSERT INTO `InstanceGlobals` (`SchemaVersion`, `ContactEmail`)
VALUES (1, 'saul.statman@sjsu.edu');
