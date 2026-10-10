-- Dialer queue + agent state schema (MySQL, used by the VICIdial-compatible app).

CREATE TABLE IF NOT EXISTS vicidial_list (
  lead_id INT AUTO_INCREMENT PRIMARY KEY,
  entry_list_id VARCHAR(32),
  phone_number VARCHAR(20) NOT NULL,
  rank INT DEFAULT 0,
  timezone_offset VARCHAR(8),
  comments VARCHAR(255),
  status VARCHAR(16) DEFAULT 'NEW',
  called_count INT DEFAULT 0,
  last_local_call_time DATETIME,
  INDEX idx_phone (phone_number),
  INDEX idx_status (status)
);

CREATE TABLE IF NOT EXISTS vicidial_live_agents (
  agent_id INT AUTO_INCREMENT PRIMARY KEY,
  user VARCHAR(20) NOT NULL,
  status VARCHAR(16) DEFAULT 'READY',
  lead_id INT,
  call_start DATETIME,
  calls_today INT DEFAULT 0,
  UNIQUE KEY uq_user (user)
);

CREATE TABLE IF NOT EXISTS recording_log (
  recording_id INT AUTO_INCREMENT PRIMARY KEY,
  lead_id INT,
  user VARCHAR(20),
  filename VARCHAR(255),
  length_in_sec INT DEFAULT 0,
  start_time DATETIME,
  INDEX idx_lead (lead_id)
);
