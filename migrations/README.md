# Database migrations

The app checks the schema version when it starts (`db.py`), so the database and the code must always be on the same version. When `schema.sql` changes, every database that still has the old version has to move too.

## Version 1 to version 2

Version 2 replaces the old tables, so this move **deletes all data**: users, sessions, lists, and tasks. The team agreed to reset the test data (Nov 24), so everyone signs up again afterward.

Run the steps on purpose, one at a time, and check each result before you go on (CS174-10, slide 64). Move the shared database right after the version 2 PR merges, because the new code won't start while the database is still version 1.

### Set up your terminal

Set these once in your terminal. For the shared database, use the user and the database name from the pinned message in our group chat. The shared server needs the MySQL 8.4 client.

```bash
MYSQL=/opt/homebrew/opt/mysql-client@8.4/bin/mysql
MYSQLDUMP=/opt/homebrew/opt/mysql-client@8.4/bin/mysqldump
DBHOST=robertnicholson.info
DBUSER=TEAM_USER
DB=TEAM_DB
```

Replace `TEAM_USER` and `TEAM_DB` before you press Enter. Every command below asks for the password. Type it only at that prompt, never on the command line or in a file.

### The steps

1. **Tell the team** in the group chat that the shared database is moving to version 2, and not to use it for about 10 minutes.

2. **Check that this is the right database, and that it's still version 1.**

   ```bash
   $MYSQL -h $DBHOST -u $DBUSER -p $DB -e "SELECT DATABASE(); SELECT SchemaVersion FROM InstanceGlobals; SHOW TABLES;"
   ```

   You should see our database's name, `1`, and six tables. If it says `2`, the move is already done. If anything else looks different, stop and ask in the group chat.

3. **Back up.** The backup has emails and password hashes, so it stays outside the repo and never goes into Git.

   ```bash
   mkdir -p ~/dac-backups
   $MYSQLDUMP -h $DBHOST -u $DBUSER -p --single-transaction --no-tablespaces --skip-add-locks --set-gtid-purged=OFF $DB > ~/dac-backups/$DB-v1.sql
   grep -c "CREATE TABLE" ~/dac-backups/$DB-v1.sql
   ```

   The last command must print `6`. If it doesn't, stop here.

   Why the options:
   - `--single-transaction` copies all tables at one moment without locking them.
   - `--no-tablespaces` avoids an error when the account has no PROCESS privilege.
   - `--skip-add-locks` lets an account without the LOCK TABLES privilege load the backup again.
   - `--set-gtid-purged=OFF` is needed when the server has GTIDs turned on. Without it, mysqldump asks for the RELOAD privilege and fails with ERROR 1227. It also keeps the backup loadable by our account.

4. **Remove the version 1 tables.**

   ```bash
   $MYSQL -h $DBHOST -u $DBUSER -p $DB < migrations/v1_to_v2.sql
   ```

5. **Build version 2.**

   ```bash
   $MYSQL -h $DBHOST -u $DBUSER -p $DB < schema.sql
   ```

6. **Check.**

   ```bash
   $MYSQL -h $DBHOST -u $DBUSER -p $DB -e "SHOW TABLES; SELECT SchemaVersion FROM InstanceGlobals;"
   ```

   You should see `InstanceGlobals`, `Items`, `ListMembers`, `Lists`, `Sessions`, `Users`, and `2`.

7. **Tell the team** that the shared database is on version 2. Everyone pulls `main` and signs up again, because the old accounts are gone.

### If something goes wrong

Put version 1 back from the backup. First remove any version 2 tables, then load the backup:

```bash
$MYSQL -h $DBHOST -u $DBUSER -p $DB -e "DROP TABLE IF EXISTS Items, ListMembers, Sessions, Lists, Users, InstanceGlobals"
$MYSQL -h $DBHOST -u $DBUSER -p $DB < ~/dac-backups/$DB-v1.sql
```

Then run step 2 again. It should say `1`.

### Practice on your own computer first

Do the whole move on your own `dac_dev` before you touch the shared database. Set the variables for your local MySQL, make `dac_dev` a version 1 database again (from commit `620a3d3`, the last `main` with version 1), and add a test user:

```bash
MYSQL=mysql
MYSQLDUMP=mysqldump
DBHOST=localhost
DBUSER=dac
DB=dac_dev
$MYSQL -u $DBUSER -p -e "DROP DATABASE IF EXISTS dac_dev; CREATE DATABASE dac_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;"
git show 620a3d3:schema.sql | $MYSQL -u $DBUSER -p $DB
$MYSQL -u $DBUSER -p $DB -e "INSERT INTO Users (Name, Email, HashedPass, Color) VALUES ('practice', 'practice@example.com', 'x', '000000')"
```

Then do steps 2 to 6 exactly as written above. The practice works when step 6 shows version `2` and `flask --app app run --port 5001` starts the app.
