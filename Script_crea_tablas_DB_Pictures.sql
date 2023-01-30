CREATE TABLE pictures (
    id int NOT NULL AUTO_INCREMENT,
    path TEXT NOT NULL,
    date varchar(25) NOT NULL,
    PRIMARY KEY (id)
);


CREATE TABLE tags (
    tag varchar(32) NOT NULL,
    picture_id int NOT NULL,
    confidence float,
    date varchar(25) NOT NULL,
    PRIMARY KEY (tag, picture_id),
    FOREIGN KEY (picture_id) REFERENCES pictures(id)
);
