-- ==============================================================================
-- MyMiniCloud Database Initialization Script
-- ==============================================================================

-- 1. Create Baseline Database 'minicloud' & Table 'notes' (Yêu cầu cơ sở)
CREATE DATABASE IF NOT EXISTS minicloud CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE minicloud;

CREATE TABLE IF NOT EXISTS notes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO notes (title) VALUES ('Hello from MariaDB!');

-- 2. Create Extended Database 'studentdb' & Table 'students' (Chức năng mở rộng 3)
CREATE DATABASE IF NOT EXISTS studentdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE studentdb;

CREATE TABLE IF NOT EXISTS students (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id VARCHAR(10) NOT NULL UNIQUE,
  fullname VARCHAR(100) NOT NULL,
  dob DATE NOT NULL,
  major VARCHAR(50) NOT NULL,
  gpa DECIMAL(3,2) DEFAULT 3.00,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO students (student_id, fullname, dob, major, gpa) VALUES
('SV001', 'Nguyen Van An', '2004-03-15', 'Cloud Computing & DevOps', 3.85),
('SV002', 'Tran Thi Bich', '2004-07-22', 'Software Engineering', 3.72),
('SV003', 'Le Hoang Cuong', '2003-11-05', 'Information Security', 3.90),
('SV004', 'Pham Minh Duc', '2004-01-30', 'Artificial Intelligence', 3.65),
('SV005', 'Doan Phuong Thao', '2004-09-18', 'Computer Networks', 3.80)
ON DUPLICATE KEY UPDATE fullname=VALUES(fullname);

-- 3. Grant privileges to application user 'clouduser'
GRANT ALL PRIVILEGES ON studentdb.* TO 'clouduser'@'%';
GRANT ALL PRIVILEGES ON minicloud.* TO 'clouduser'@'%';
FLUSH PRIVILEGES;
