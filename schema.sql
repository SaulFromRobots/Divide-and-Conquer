-- schema.sql, version 2

-- Changes from version 1:
--   ListMembers replaces Lists.Owners and Lists.Collaborators.
--   A list can have many tasks, and a task can have no assignee.
--   Every foreign key has an ON DELETE rule.
--   MembershipChanges is gone, because we skip invitations for now.
-- Run it on an empty database:
--   mysql -u dac -p dac_dev < schema.sql
-- The app checks the version in this table when it starts.
CREATE TABLE `InstanceGlobals` (
  `SchemaVersion` int NOT NULL,
  `ContactEmail` mediumtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Users keeps its column names, so models/users.py works without changes.
-- Name uses utf8mb4_0900_ai_ci on purpose. "Saul", "saul", and "SAUL"
-- are the same user, and accents are ignored too (team decision, Nov 24).
CREATE TABLE `Users` (
  `ID` int unsigned NOT NULL AUTO_INCREMENT,
  `Name` varchar(256) NOT NULL,
  `Email` mediumtext NOT NULL,
  `HashedPass` varchar(255) NOT NULL,
  `Color` varchar(6) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Name_UNIQUE` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Sessions has a foreign key to Users, so it comes after Users.
-- When a user is deleted, their sessions are deleted too.
CREATE TABLE `Sessions` (
  `ID` int unsigned NOT NULL AUTO_INCREMENT,
  `UserID` int unsigned NOT NULL,
  `Token` varchar(256) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `LastUsed` timestamp NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Token_UNIQUE` (`Token`),
  KEY `UserID_INDEX` (`UserID`),
  CONSTRAINT `fk_sessions_user` FOREIGN KEY (`UserID`) REFERENCES `Users` (`ID`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `Lists` (
  `ID` int unsigned NOT NULL AUTO_INCREMENT,
  `Name` mediumtext NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ListMembers has one row per list and user, with one role.
-- The primary key stops the same user from joining a list twice.
-- Deleting a list deletes its members (team decision, Nov 24).
-- Deleting a user who is still in a list fails (RESTRICT), so no list
-- loses its last owner that way.
-- Keep the enum order. MySQL numbers the values 1 and 2, the same as
-- ROLES in models/members.py.
CREATE TABLE `ListMembers` (
  `ListID` int unsigned NOT NULL,
  `UserID` int unsigned NOT NULL,
  `Role` enum('Owner','Colab') NOT NULL,
  PRIMARY KEY (`ListID`,`UserID`),
  KEY `UserID_INDEX` (`UserID`),
  CONSTRAINT `fk_listmembers_list` FOREIGN KEY (`ListID`) REFERENCES `Lists` (`ID`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_listmembers_user` FOREIGN KEY (`UserID`) REFERENCES `Users` (`ID`)
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Items has foreign keys to Lists and Users, so it comes after both.
-- One ID for all tasks, and a list can have many tasks.
-- Assignee is NULL when nobody is assigned. The route checks that the
-- assignee is a member of the list. If that user is deleted, the task
-- stays and becomes unassigned (SET NULL).
-- Deleting a list deletes its tasks (team decision, Nov 24).
-- The (ListID, OrderPlacement) index finds the tasks of a list in order.
-- OrderPlacement may have gaps.
-- Keep the State order too. MySQL numbers the values 1, 2, and 3, the same
-- as STATES in models/items.py.
CREATE TABLE `Items` (
  `ID` int unsigned NOT NULL AUTO_INCREMENT,
  `ListID` int unsigned NOT NULL,
  `Text` mediumtext NOT NULL,
  `Assignee` int unsigned DEFAULT NULL,
  `State` enum('No progress','In progress','Done') NOT NULL DEFAULT 'No progress',
  `OrderPlacement` int NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `ListID_Order_INDEX` (`ListID`,`OrderPlacement`),
  KEY `Assignee_INDEX` (`Assignee`),
  CONSTRAINT `fk_items_list` FOREIGN KEY (`ListID`) REFERENCES `Lists` (`ID`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_items_assignee` FOREIGN KEY (`Assignee`) REFERENCES `Users` (`ID`)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- SchemaVersion must match SCHEMA_VERSION in db.py.
INSERT INTO `InstanceGlobals` (`SchemaVersion`, `ContactEmail`)
VALUES (2, 'saul.statman@sjsu.edu');
