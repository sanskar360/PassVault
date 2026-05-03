CREATE TABLE passwords(
	id INT NOT NULL AUTO_INCREMENT,
	pass_name VARCHAR(250) NOT NULL,
    pass_word VARCHAR(250) NOT NULL,
    PRIMARY KEY (id),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users1(id)
);
    
    