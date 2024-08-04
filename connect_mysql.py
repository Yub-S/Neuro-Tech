import mysql.connector

connection = mysql.connector.connect(
    host='localhost',
    database='hospital',
    user='root',
    password='nepal2015'
)

def book_appointment(patient_info):
    
    if connection.is_connected():
        cursor = connection.cursor()

        # Extract patient information
        doctor_name = patient_info['doctor']
        preferred_day = patient_info['preferred_day']
        preferred_time = patient_info['preferred_time']

        # Check if the preferred day and time are already booked for the doctor
        check_query = """SELECT * FROM patients 
                         WHERE doctor_booked = %s AND appointment_day = %s AND appointment_time = %s"""
        cursor.execute(check_query, (doctor_name, preferred_day, preferred_time))
        result = cursor.fetchone()

        if result:
            # The time slot is already booked
            print("The selected time slot on {} at {} is already booked. Please choose another time slot.".format(preferred_day, preferred_time))
        else:
            # The time slot is available, proceed with booking
            insert_query = """INSERT INTO patients (full_name, problem, contact, doctor_booked, appointment_day, appointment_time) 
                              VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(insert_query, (
                patient_info['name'], 
                patient_info['problem'], 
                patient_info['contact'], 
                doctor_name, 
                preferred_day, 
                preferred_time
            ))
            connection.commit()

            print("Appointment booked successfully for {} on {} at {}.".format(patient_info['name'], preferred_day, preferred_time))

        connection.close()

def reschedule_appointment(new_info):
    
    if connection.is_connected():
        cursor = connection.cursor()

        # Fetch the current appointment details
        fetch_query = """SELECT doctor_booked, appointment_day, appointment_time 
                         FROM patients WHERE full_name = %s"""
        cursor.execute(fetch_query, (new_info['patient_name'],))
        result = cursor.fetchone()
        
        if result:
            doctor_name, current_day, current_time = result

            # Check if the new day and time slot are already booked for the same doctor
            check_query = """SELECT * FROM patients 
                             WHERE doctor_booked = %s AND appointment_day = %s AND appointment_time = %s"""
            cursor.execute(check_query, (doctor_name, new_info['new_day'], new_info['new_time']))
            check_result = cursor.fetchone()

            if check_result:
                # New time slot is already booked
                print("The selected new time slot on {} at {} is already booked. Please choose another time slot.".format(new_info['new_day'], new_info['new_time']))
            else:
                # The new time slot is available, proceed with rescheduling
                update_patient_query = """UPDATE patients 
                                          SET appointment_day = %s, appointment_time = %s 
                                          WHERE full_name = %s"""
                cursor.execute(update_patient_query, (new_info['new_day'], new_info['new_time'], new_info['patient_name']))
                connection.commit()

                print("Appointment rescheduled successfully to {} on {}.".format(new_info['new_time'], new_info['new_day']))
        else:
            print("Patient not found.")

        connection.close()

          
def cancel_appointment(patient_name):
    connection = mysql.connector.connect(
        host='localhost',
        database='hospital',
        user='root',
        password='nepal2015'
    )

    if connection.is_connected():
        cursor = connection.cursor()

        # Fetch the current appointment details for the patient
        fetch_query = """SELECT doctor_booked, appointment_day, appointment_time 
                         FROM patients WHERE full_name = %s"""
        cursor.execute(fetch_query, (patient_name,))
        result = cursor.fetchone()
        
        if result:
            doctor_name, appointment_day, appointment_time = result

            # Remove the patient's appointment from the patients table
            delete_patient_query = """DELETE FROM patients WHERE full_name = %s"""
            cursor.execute(delete_patient_query, (patient_name,))
            
            # Commit the changes
            connection.commit()

            print(f"Appointment with  {doctor_name} on {appointment_day} at {appointment_time} canceled successfully.")
        else:
            print("Patient not found.")
        
        connection.close()

# Function to retrieve doctors' information from the database
def retrieve_database_info():
    if connection.is_connected():
        doctor_list = []
        if connection.is_connected():
            cursor = connection.cursor()
            query = 'SELECT * FROM doctors'
            cursor.execute(query)
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            doctor_list = [dict(zip(column_names, row)) for row in rows]
            cursor.close()
            connection.close()
        doctors_info = '\n'.join([str(doctor) for doctor in doctor_list])
        return doctors_info

# doctors_info = retrieve_database_info()

patient_info = {"name": "John Doe","contact": "123-456-7890", "problem": "Headache", "preferred_day": "Monday","preferred_time":"2:00 PM-3:00 PM", "doctor": "Dr. Smith"}
new_info = {"patient_name":"John Doe","new_day":"Wednesday","new_time":"11:00 AM - 12:00 PM"}
patient_name='John Doe'
cancel_appointment(patient_name)