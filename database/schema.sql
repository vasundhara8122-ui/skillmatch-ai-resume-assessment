-- SkillMatch AI Database Schema (MySQL)
-- Compatible with Aiven MySQL and standard MySQL 8.x

CREATE DATABASE IF NOT EXISTS skillmatch_ai;
USE skillmatch_ai;

CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    degree VARCHAR(255),
    graduation_year VARCHAR(20),
    level VARCHAR(20) DEFAULT 'Level 1',
    password VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    raw_text LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

CREATE TABLE IF NOT EXISTS skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS candidate_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    skill_id INT NOT NULL,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id)
);

CREATE TABLE IF NOT EXISTS assessments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    level VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    invitation_sent BOOLEAN DEFAULT FALSE,
    started_at TIMESTAMP NULL,
    submitted_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    skill VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    level VARCHAR(20) DEFAULT 'Level 1',
    question TEXT NOT NULL,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_answer TEXT,
    reference_code TEXT,
    test_input TEXT,
    expected_output TEXT,
    points INT DEFAULT 1
);

CREATE TABLE IF NOT EXISTS assessment_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assessment_id INT NOT NULL,
    question_id INT NOT NULL,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

CREATE TABLE IF NOT EXISTS answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assessment_id INT NOT NULL,
    question_id INT NOT NULL,
    candidate_answer TEXT,
    is_correct BOOLEAN DEFAULT FALSE,
    points_earned INT DEFAULT 0,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

CREATE TABLE IF NOT EXISTS skill_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assessment_id INT NOT NULL,
    skill VARCHAR(100) NOT NULL,
    theory_score FLOAT DEFAULT 0,
    coding_score FLOAT DEFAULT 0,
    total FLOAT DEFAULT 0,
    percentage FLOAT DEFAULT 0,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id)
);

CREATE TABLE IF NOT EXISTS results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assessment_id INT NOT NULL,
    overall_score FLOAT DEFAULT 0,
    theory_score FLOAT DEFAULT 0,
    coding_score FLOAT DEFAULT 0,
    mcq_score FLOAT DEFAULT 0,
    sql_score FLOAT DEFAULT 0,
    code_output_score FLOAT DEFAULT 0,
    debugging_score FLOAT DEFAULT 0,
    total_questions INT DEFAULT 0,
    correct_count INT DEFAULT 0,
    percentage FLOAT DEFAULT 0,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id)
);

CREATE TABLE IF NOT EXISTS job_roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS job_role_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    skill VARCHAR(100) NOT NULL,
    weight FLOAT DEFAULT 1.0,
    FOREIGN KEY (role_id) REFERENCES job_roles(id)
);

CREATE TABLE IF NOT EXISTS skill_matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assessment_id INT NOT NULL,
    role_name VARCHAR(100) NOT NULL,
    match_percentage FLOAT DEFAULT 0,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id)
);

CREATE TABLE IF NOT EXISTS email_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT,
    to_email VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    body TEXT,
    status VARCHAR(100),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);
