import mysql.connector

# Establish a database connection
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="DB_password"
)

cursor = db_connection.cursor()

# Drop the database if it exists
cursor.execute("DROP DATABASE IF EXISTS hospital")

# Create a new database
cursor.execute("CREATE DATABASE hospital")

# Select the new database
cursor.execute("USE hospital")

# Create the doctors table
cursor.execute("""
    CREATE TABLE doctors (
        full_name VARCHAR(255) NOT NULL,
        availability_days VARCHAR(255) NOT NULL,
        availability_time VARCHAR(255) NOT NULL,
        specialization VARCHAR(255) NOT NULL
    )
""")

# Insert data into the doctors table
doctors_data = [
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
    ('Dr. Laura Harris', 'Monday to Friday', '10:00 AM - 12:00 PM, 1:00 PM - 3:00 PM', 'Radiology')
]

cursor.executemany("""
    INSERT INTO doctors (full_name, availability_days, availability_time, specialization)
    VALUES (%s, %s, %s, %s)
""", doctors_data)

# Create the patients table
cursor.execute("""
    CREATE TABLE patients (
        full_name VARCHAR(100),
        problem VARCHAR(255),
        email VARCHAR(255),
        doctor_booked VARCHAR(100),
        appointment_day VARCHAR(50),
        appointment_time VARCHAR(50)
    )
""")

# Select data from both tables
cursor.execute("SELECT * FROM doctors")
doctors_result = cursor.fetchall()
print("Doctors Table:")
for row in doctors_result:
    print(row)

cursor.execute("SELECT * FROM patients")
patients_result = cursor.fetchall()
print("\nPatients Table:")
for row in patients_result:
    print(row)

# Commit and close the connection
db_connection.commit()
cursor.close()
db_connection.close()
