-- assume this was already done: CREATE DATABASE photoapp;
-- users table:
    -- userid (primary key)
    -- firstname
    -- lastname
    -- email

-- CREATE DATABASE studyhelper;
USE studyhelper;

DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS projectdocs;
DROP TABLE IF EXISTS conversations;

CREATE TABLE users
(
    userid       int not null AUTO_INCREMENT,
    email        varchar(128) not null,
    lastname     varchar(64) not null,
    firstname    varchar(64) not null,
    -- bucketfolder varchar(48) not null,  -- random, unique name (UUID)
    PRIMARY KEY (userid),
    UNIQUE      (email)
);

ALTER TABLE users AUTO_INCREMENT = 80001;  -- starting value

-- projects table:
    -- projectid (primary key)
    -- userid (foreign key references users.userid)
    -- projectname
    -- bucketfolder 
CREATE TABLE projects
(
    projectid      int not null AUTO_INCREMENT,
    userid         int not null,
    projectname    varchar(128) not null,  -- original name from user
    bucketfolder   varchar(128) not null,  -- random, unique name in bucket
    PRIMARY KEY (projectid),
    FOREIGN KEY (userid) REFERENCES users(userid),
    UNIQUE        (bucketfolder)
);

ALTER TABLE projects AUTO_INCREMENT = 1001;  -- starting value

-- projectdocs table:
    -- filename
    -- projectid (foreign key) 
    -- Compound primary key (filename, projectid)
CREATE TABLE projectdocs
(
    filename    varchar(128) not null,
    projectid   int not null,
    PRIMARY KEY (filename, projectid),
    FOREIGN KEY (projectid) REFERENCES projects(projectid)
);

-- conversations table:
    -- projectid (primary key, foreign key references projects.projectid)
    -- timestamp when message was sent
    -- role  (who sent the message (“user” or “assistant”)
    -- message (contents of the message)
CREATE TABLE conversations
(
    projectid   int not null,
    timestamp   timestamp not null,
    role        varchar(16) not null,
    message     varchar(1024) not null,
    PRIMARY KEY (projectid, timestamp),
    FOREIGN KEY (projectid) REFERENCES projects(projectid)
);

-- DONE