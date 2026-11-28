-- migrations/v1_to_v2.sql
-- Removes the version 1 tables. Run schema.sql right after it to build
-- version 2. The steps are in migrations/README.md.
--
-- WARNING: this deletes ALL data in these tables (users, sessions, lists,
-- and tasks). Back up first, and run it only on purpose.
-- The team agreed on Nov 24 to reset the test data, so everyone signs up again.
--
-- One DROP TABLE statement removes all six tables or none of them (InnoDB).
-- The child tables come first in the list, before the tables they point to.
-- IF EXISTS makes it safe to run again after the tables are gone.
-- On a version 2 database it stops with ERROR 3730 and changes nothing,
-- because ListMembers still points to Lists and Users.
DROP TABLE IF EXISTS
  `Items`,
  `Sessions`,
  `MembershipChanges`,
  `Lists`,
  `Users`,
  `InstanceGlobals`;
