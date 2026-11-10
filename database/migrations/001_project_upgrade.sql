-- Run once against the existing campus_events database.
-- If your users.section column already has enough width, the ALTER is harmless.
USE campus_events;
ALTER TABLE users MODIFY section VARCHAR(20) NOT NULL;
ALTER TABLE users ADD COLUMN year_of_study VARCHAR(20) NULL;
ALTER TABLE team_members MODIFY section VARCHAR(20) NOT NULL;
UPDATE users SET year_of_study=section WHERE year_of_study IS NULL;
ALTER TABLE sub_events ADD COLUMN venue VARCHAR(255) NULL;
CREATE TABLE IF NOT EXISTS workshop_sessions (
 id INT AUTO_INCREMENT PRIMARY KEY, event_id INT NOT NULL,
 session_date DATE NOT NULL, session_title VARCHAR(200) NOT NULL DEFAULT 'Workshop Session',
 created_by_staff_id INT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
 FOREIGN KEY (created_by_staff_id) REFERENCES staff(id) ON DELETE SET NULL,
 UNIQUE KEY unique_workshop_session (event_id, session_date, session_title)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS session_attendance (
 id INT AUTO_INCREMENT PRIMARY KEY, session_id INT NOT NULL, registration_id INT NOT NULL,
 attendance_status ENUM('present','absent') NOT NULL DEFAULT 'absent',
 marked_by_staff_id INT NULL, marked_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 FOREIGN KEY (session_id) REFERENCES workshop_sessions(id) ON DELETE CASCADE,
 FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE,
 FOREIGN KEY (marked_by_staff_id) REFERENCES staff(id) ON DELETE SET NULL,
 UNIQUE KEY unique_session_attendance (session_id, registration_id)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS presentation_scores (
 id INT AUTO_INCREMENT PRIMARY KEY, registration_id INT NOT NULL, staff_id INT NOT NULL,
 score DECIMAL(5,2) NOT NULL, max_score DECIMAL(5,2) NOT NULL DEFAULT 100, feedback TEXT,
 updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE,
 FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE,
 UNIQUE KEY unique_presentation_score (registration_id, staff_id)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS sub_event_staff (
 id INT AUTO_INCREMENT PRIMARY KEY, sub_event_id INT NOT NULL, staff_id INT NOT NULL,
 assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (sub_event_id) REFERENCES sub_events(id) ON DELETE CASCADE,
 FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE,
 UNIQUE KEY unique_sub_event_staff (sub_event_id, staff_id)
) ENGINE=InnoDB;

