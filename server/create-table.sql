CREATE DATABASE studyhelper;

USE studyhelper;

DROP TABLE IF EXISTS projects;

DROP TABLE IF EXISTS users;

DROP TABLE IF EXISTS projectdocs;

DROP TABLE IF EXISTS conversations;

CREATE TABLE users (
    userid int not null AUTO_INCREMENT,
    email varchar(128) not null,
    lastname varchar(64) not null,
    firstname varchar(64) not null,
    PRIMARY KEY (userid),
    UNIQUE (email)
);

ALTER TABLE users AUTO_INCREMENT = 80001;

CREATE TABLE projects (
    projectid int not null AUTO_INCREMENT,
    userid int not null,
    projectname varchar(128) not null, -- original name from user
    bucketfolder varchar(128) not null, -- random, unique name in bucket
    PRIMARY KEY (projectid),
    FOREIGN KEY (userid) REFERENCES users (userid),
);

ALTER TABLE projects AUTO_INCREMENT = 1001;

CREATE TABLE projectdocs (
    filename varchar(510) not null,
    originalfilename varchar(255) null,
    projectid int not null,
    PRIMARY KEY (filename, projectid),
    FOREIGN KEY (projectid) REFERENCES projects (projectid)
);

CREATE TABLE conversations (
    projectid int not null,
    timestamp timestamp not null,
    role varchar(16) not null,
    message LONGTEXT not null,
    PRIMARY KEY (projectid, timestamp),
    FOREIGN KEY (projectid) REFERENCES projects (projectid)
);

-- DONE