-- Database setup for interview platform
-- Run this in your PostgreSQL database

-- Create the database (run this first)
-- CREATE DATABASE interviews;

-- Connect to the interviews database and run the following:

-- Table for storing Round 1 questions
CREATE TABLE IF NOT EXISTS round1_questions (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    difficulty VARCHAR(20) NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
    question_text TEXT NOT NULL,
    options JSONB NOT NULL,
    correct_answer VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing Round 1 results
CREATE TABLE IF NOT EXISTS round1_results (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    score INTEGER NOT NULL,
    correct INTEGER NOT NULL,
    wrong INTEGER NOT NULL,
    category_breakdown JSONB,
    difficulty_mix JSONB,
    duration INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pass', 'reject', 'review')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for anti-cheat logging
CREATE TABLE IF NOT EXISTS round1_logs (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    event_type VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample questions for testing
INSERT INTO round1_questions (category, difficulty, question_text, options, correct_answer) VALUES
-- Easy Questions
('aptitude', 'easy', 'What is 15 + 27?', '{"A": "40", "B": "42", "C": "38", "D": "45"}', 'B'),
('reasoning', 'easy', 'If all cats are animals, and Fluffy is a cat, then Fluffy is:', '{"A": "Not an animal", "B": "An animal", "C": "Maybe an animal", "D": "Cannot determine"}', 'B'),
('reading', 'easy', 'What does "ubiquitous" mean?', '{"A": "Rare", "B": "Present everywhere", "C": "Expensive", "D": "Difficult"}', 'B'),
('aptitude', 'easy', 'What is 8 × 7?', '{"A": "54", "B": "56", "C": "58", "D": "52"}', 'B'),

-- Medium Questions
('reasoning', 'medium', 'If A > B and B > C, then:', '{"A": "A > C", "B": "A < C", "C": "A = C", "D": "Cannot determine"}', 'A'),
('aptitude', 'medium', 'A train travels 120 km in 2 hours. What is its speed?', '{"A": "60 km/h", "B": "40 km/h", "C": "80 km/h", "D": "100 km/h"}', 'A'),
('reading', 'medium', 'In the context of software development, what does "API" stand for?', '{"A": "Application Programming Interface", "B": "Advanced Programming Integration", "C": "Automated Process Interface", "D": "Application Process Integration"}', 'A'),

-- Hard Questions
('reasoning', 'hard', 'In a room with 30 people, if everyone shakes hands with everyone else exactly once, how many handshakes occur?', '{"A": "435", "B": "450", "C": "420", "D": "465"}', 'A'),
('aptitude', 'hard', 'If a number is increased by 20% and then decreased by 20%, the result is:', '{"A": "Same as original", "B": "4% less than original", "C": "4% more than original", "D": "Cannot determine"}', 'B'),
('reading', 'hard', 'What is the time complexity of binary search?', '{"A": "O(n)", "B": "O(log n)", "C": "O(n²)", "D": "O(1)"}', 'B');

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_round1_results_email ON round1_results(email);
CREATE INDEX IF NOT EXISTS idx_round1_results_created_at ON round1_results(created_at);
CREATE INDEX IF NOT EXISTS idx_round1_logs_email ON round1_logs(email);
