DROP TABLE IF EXISTS UserAccounts;
DROP TABLE IF EXISTS Tweets;
DROP TABLE IF EXISTS UserFollows;

CREATE TABLE  UserAccounts (
  username          TEXT NOT NULl,
  password          TEXT NOT NULl,
  email             TEXT NOT NULl,
  PRIMARY KEY (username)
);



CREATE TABLE Tweets (
    tweet_id        integer,
    username        TEXT NOT NULL,
    textEntry       TEXT NOT NULL,
    timestamp       INTEGER DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tweet_id),
    FOREIGN KEY (username) REFERENCES UserAccounts(username)


);

CREATE TABLE UserFollows (
    followed        TEXT NOT NULL,
    follower        TEXT NOT NULL,
    FOREIGN KEY (follower) REFERENCES UserAccounts(username)
);


INSERT INTO UserAccounts (username, password, email)
VALUES
("Brandon1", "password1", "brandon1@gmail.com"),
("Brandon2", "password2", "brandon2@gmail.com"),
("Brandon3", "password3", "brandon3@gmail.com"),
("Brandon4", "password4", "brandon4@gmail.com");


INSERT INTO UserFollows (followed, follower)
VALUES
("Brandon1", "Brandon2"),
("Brandon1", "Brandon3"),
("Brandon1", "Brandon4"),
("Brandon2", "Brandon1"),
("Brandon2", "Brandon3"),
("Brandon2", "Brandon4"),
("Brandon3", "Brandon2"),
("Brandon3", "Brandon4"),
("Brandon4", "Brandon1");

INSERT INTO Tweets (username, textEntry)
VALUES
("Brandon1", "1!!!"),
("Brandon2", "2!!!"),
("Brandon3", "3!!!"),
("Brandon4", "4!!!");
