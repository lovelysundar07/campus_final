-- ============================================================
-- MS College - Campus Events & Workshop Management System
-- MySQL Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS campus_events CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE campus_events;

-- ============================================================
-- USERS TABLE (Students / Participants)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    roll_no VARCHAR(30) NOT NULL UNIQUE,
    dept VARCHAR(100) NOT NULL,
    section VARCHAR(20) NOT NULL,
    year_of_study VARCHAR(20) NULL,
    profile_image VARCHAR(255) NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(15),
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('participant') DEFAULT 'participant',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- ADMIN TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Default admin: admin@msvcollege.ac.in / admin123
-- (Password hash will be inserted by app.py init)

-- ============================================================
-- STAFF TABLE (Incharge Staff)
-- ============================================================
CREATE TABLE IF NOT EXISTS staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(15),
    profile_image VARCHAR(255) NULL,
    designation VARCHAR(100),
    department VARCHAR(100),
    password_hash VARCHAR(255) NOT NULL,
    is_approved BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- EVENTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    event_type VARCHAR(50) NOT NULL DEFAULT 'other',
    description TEXT,
    event_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    venue VARCHAR(255) NOT NULL,
    capacity INT DEFAULT 100,
    registration_deadline DATE,
    banner_image VARCHAR(255),
    status ENUM('upcoming', 'ongoing', 'completed', 'cancelled') DEFAULT 'upcoming',
    is_published BOOLEAN DEFAULT FALSE,
    results_published BOOLEAN NOT NULL DEFAULT FALSE,
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES admins(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================================
-- SUB-EVENTS TABLE (for Symposiums)
-- ============================================================
CREATE TABLE IF NOT EXISTS sub_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    allowed_teams INT DEFAULT 10,
    min_team_size INT DEFAULT 1,
    max_team_size INT DEFAULT 4,
    venue VARCHAR(255) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- EVENT INCHARGE (Staff assigned to Events)
-- ============================================================
CREATE TABLE IF NOT EXISTS event_incharge (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    staff_id INT NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE,
    UNIQUE KEY unique_assignment (event_id, staff_id)
) ENGINE=InnoDB;

-- ============================================================
-- REGISTRATIONS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    sub_event_id INT,
    team_name VARCHAR(150),
    ppt_file_path VARCHAR(500),
    attendance_status ENUM('pending', 'present', 'absent') DEFAULT 'pending',
    certificate_issued BOOLEAN DEFAULT FALSE,
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (sub_event_id) REFERENCES sub_events(id) ON DELETE SET NULL,
    UNIQUE KEY unique_registration (user_id, event_id, sub_event_id)
) ENGINE=InnoDB;

-- ============================================================
-- TEAM MEMBERS TABLE (for Symposiums)
-- ============================================================
CREATE TABLE IF NOT EXISTS team_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    registration_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    roll_no VARCHAR(30) NOT NULL,
    dept VARCHAR(100) NOT NULL,
    section VARCHAR(20) NOT NULL,
    is_leader BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- CERTIFICATES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS certificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    registration_id INT NOT NULL UNIQUE,
    certificate_path VARCHAR(500),
    certificate_number VARCHAR(100) UNIQUE,
    issued_by INT,
    issued_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE,
    FOREIGN KEY (issued_by) REFERENCES admins(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================================
-- EVENT REPORTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS event_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    generated_by INT NOT NULL,
    report_path VARCHAR(500),
    total_registered INT DEFAULT 0,
    total_present INT DEFAULT 0,
    notes TEXT,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (generated_by) REFERENCES staff(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- AI CHAT LOGS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS ai_chat_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    user_type ENUM('participant', 'staff', 'admin') DEFAULT 'participant',
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    language ENUM('en', 'ta') DEFAULT 'en',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================================
-- NOTIFICATIONS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_status ON events(status);
CREATE INDEX idx_events_published ON events(is_published);
CREATE INDEX idx_registrations_user ON registrations(user_id);
CREATE INDEX idx_registrations_event ON registrations(event_id);
CREATE INDEX idx_staff_approved ON staff(is_approved);

-- ============================================================
-- DEFAULT ADMIN ACCOUNT (password: Admin@MSV2024)
-- Note: The app will hash this on first run via init_db()
-- ============================================================
-- INSERT INTO admins (name, email, password_hash) VALUES 
-- ('MSV Admin', 'admin@msvcollege.ac.in', '<hashed_by_app>');


-- Additional operational tables for daily attendance and PPT scoring.
-- Existing one-time attendance_status remains for backward compatibility.
CREATE TABLE IF NOT EXISTS workshop_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    session_date DATE NOT NULL,
    session_title VARCHAR(200) NOT NULL DEFAULT 'Workshop Session',
    created_by_staff_id INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by_staff_id) REFERENCES staff(id) ON DELETE SET NULL,
    UNIQUE KEY unique_workshop_session (event_id, session_date, session_title)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS session_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    registration_id INT NOT NULL,
    attendance_status ENUM('present','absent') NOT NULL DEFAULT 'absent',
    marked_by_staff_id INT NULL,
    marked_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES workshop_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE,
    FOREIGN KEY (marked_by_staff_id) REFERENCES staff(id) ON DELETE SET NULL,
    UNIQUE KEY unique_session_attendance (session_id, registration_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS presentation_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    registration_id INT NOT NULL,
    staff_id INT NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    max_score DECIMAL(5,2) NOT NULL DEFAULT 100,
    feedback TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE,
    UNIQUE KEY unique_presentation_score (registration_id, staff_id),
    CHECK (score >= 0 AND score <= max_score)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS sub_event_staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sub_event_id INT NOT NULL,
    staff_id INT NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sub_event_id) REFERENCES sub_events(id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE,
    UNIQUE KEY unique_sub_event_staff (sub_event_id, staff_id)
) ENGINE=InnoDB;
