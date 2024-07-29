import streamlit as st
import dotenv
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import google.generativeai as genai

# Load environment variables
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

# Configure the Gemini model
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def book_appointment(doctor_name, patient_info):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='hospital',
            user='root',
            password=os.getenv('DB_PASSWORD')
        )
        if connection.is_connected():
            cursor = connection.cursor()
            fetch_query = "SELECT appointment_booked, patients_per_day FROM doctors WHERE full_name = %s"
            cursor.execute(fetch_query, (doctor_name,))
            result = cursor.fetchone()
            if result:
                current_appointments, patients_per_day = result
                if current_appointments < patients_per_day:
                    new_appointments = current_appointments + 1
                    update_query = "UPDATE doctors SET appointment_booked = %s WHERE full_name = %s"
                    cursor.execute(update_query, (new_appointments, doctor_name))
                    connection.commit()
                    query = """INSERT INTO patients (full_name, problem, doctor_booked, appointment_day) 
                               VALUES (%s, %s, %s, %s)"""
                    cursor.execute(query, (patient_info['full_name'], patient_info['problem'], doctor_name, patient_info['appointment_day']))
                    connection.commit()
                    st.success(f"Appointment booked successfully for {doctor_name}")
                else:
                    st.error(f"Doctor {doctor_name} has reached the maximum number of appointments for the day.")
            cursor.close()
        connection.close()
    except Error as e:
        st.error(f"Error: {e}")

def retrieve_database_info():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='hospital',
            user='root',
            password=os.getenv('DB_PASSWORD')
        )
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
        return doctor_list
    except Error as e:
        st.error(f"Error: {e}")
        return []

def get_gemini_response(question, doctors_info_str, custom_prompt=""):
    # Include the chat history in the message
    full_message = f"{custom_prompt}\n\nHere is the doctors' information:\n{doctors_info_str}\n\nPatient's query: {question}"
    response = chat.send_message(full_message, stream=True)
    return response

def main():
    st.title("Medical Appointment Scheduler Chatbot")

    doctors_info = retrieve_database_info()

    if doctors_info:
        doctors_info_str = '\n'.join([f"Doctor: {doctor['full_name']}, Specialization: {doctor['specialization']}, Availability: {doctor['availability_days']} {doctor['availability_time']}, Patients per Day: {doctor['patients_per_day']}, Appointments Booked: {doctor['appointment_booked']}" for doctor in doctors_info])

        st.header("Gemini LLM Chatbot")

        # Initialize session state for chat history if it doesn't exist
        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = []

        user_input = st.text_input("How can I help you?", key="input")
        submit = st.button("Submit")

        if submit and user_input:
            # Custom prompt to guide the chatbot
            custom_prompt = """You are a helpful assistant for answering questions about booking medical appointments. Ask for user's relevant personal information and then,
                You will be provided with information about doctors information.If the doctors are available based on the patient's query, you need to identify their problem, suggest relevant doctors, and assist with booking an appointment."""
            
            # Include chat history in the response
            response = get_gemini_response(user_input, doctors_info_str, custom_prompt)
            st.session_state['chat_history'].append(("You", user_input))
            st.subheader("The Response is")
            for chunk in response:
                st.write(chunk.text)
                st.session_state['chat_history'].append(("Bot", chunk.text))

            # Check if the response includes appointment booking details
            if "book an appointment" in user_input.lower():
                with st.form("appointment_form"):
                    patient_name = st.text_input("Full Name")
                    patient_problem = st.text_input("Problem")
                    specialization = st.selectbox("Specialization", list(set([doctor['specialization'] for doctor in doctors_info])))
                    filtered_doctors = [doctor for doctor in doctors_info if doctor['specialization'] == specialization]
                    doctor_name = st.selectbox("Doctor", [doctor['full_name'] for doctor in filtered_doctors])
                    appointment_day = st.date_input("Appointment Day")
                    submit_form = st.form_submit_button("Book Appointment")

                    if submit_form:
                        selected_doctor = next((doctor for doctor in doctors_info if doctor['full_name'] == doctor_name), None)
                        if selected_doctor:
                            patient_info = {
                                'full_name': patient_name,
                                'problem': patient_problem,
                                'appointment_day': appointment_day
                            }
                            book_appointment(doctor_name, patient_info)
                        else:
                            st.error(f"Doctor {doctor_name} is not available. Please choose another doctor or slot.")

        st.subheader("The Chat History is")
        for role, text in st.session_state['chat_history']:
            st.write(f"{role}: {text}")

if __name__ == "__main__":
    main()

