USE ledger;

DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  date DATE NOT NULL,
  amount INT
);
