DROP DATABASE IF EXISTS hospital;
CREATE DATABASE hospital;
USE hospital;

CREATE TABLE doctors (
    full_name VARCHAR(255) NOT NULL,
    availability_days VARCHAR(255) NOT NULL,
    availability_time VARCHAR(255) NOT NULL,
    specialization VARCHAR(255) NOT NULL
);

-- Insert 12 rows into the doctors table
INSERT INTO doctors (full_name, availability_days, availability_time, specialization)
VALUES
('Dr. Alice Smith', 'Monday to Friday', '10:00 AM - 12:00 PM, 1:00 PM - 3:00 PM', 'Cardiology'),
('Dr. Bob Johnson', 'Monday to Friday', '10:00 AM - 12:00 PM, 1:00 PM - 3:00 PM', 'Dermatology'),
('Dr. Charlie Davis', 'Monday to Friday', '10:00 AM - 12:00 PM, 1:00 PM - 3:00 PM', 'Endocrinology'),
('Dr. Diana Moore', 'Monday to Friday', '10:00 AM - 12:00 PM, 1:00 PM - 3:00 PM', 'Gastroenterology'),
('Dr. Edward Brown', 'Monday to Friday', '10:00 AM - 12:00 PM, 1:00 PM - 3:00 PM', 'Hematology'),
('Dr. Fiona Wilson', 'Monday to Friday', '10:00 AM - 12:00 PM, 1:00 PM - 3:00 PM', 'Neurology'),
('Dr. George Taylor', 'Monday to Friday', '10:00 AM - 12:00 PM, 1:00 PM - 3:00 PM', 'Oncology'),
('Dr. Helen Anderson', 'Monday to Friday', '10:00 AM - 12:00 PM, 1:00 PM - 3:00 PM', 'Ophthalmology'),
('Dr. Ian Thompson', 'Monday to Friday', '10:00 AM - 12:00 PM, 1:00 PM - 3:00 PM', 'Orthopedics'),
('Dr. Jane Martinez', 'Monday to Friday', '10:00 AM - 12:00 PM, 1:00 PM - 3:00 PM', 'Pediatrics'),
('Dr. Kevin White', 'Monday to Friday', '10:00 AM - 12:00 PM, 1:00 PM - 3:00 PM', 'Psychiatry'),
('Dr. Laura Harris', 'Monday to Friday', '10:00 AM - 12:00 PM, 1:00 PM - 3:00 PM', 'Radiology');

CREATE TABLE patients (
    full_name VARCHAR(100),
    problem VARCHAR(255),
    email VARCHAR(255),
    doctor_booked VARCHAR(100),
    appointment_day VARCHAR(50),
    appointment_time VARCHAR(50)
);
