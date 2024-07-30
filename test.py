import openai
import os
from dotenv import load_dotenv
import streamlit as st
import mysql.connector
import json

# Load environment variables
load_dotenv()
AI71_BASE_URL = "https://api.ai71.ai/v1/"

api_key = os.getenv('AI71_API_KEY')
client = openai.OpenAI(api_key=api_key, base_url=AI71_BASE_URL)

st.title("Appointment-Scheduler")

# Book appointment function
def book_appointment(doctor_name, patient_info):
    connection = mysql.connector.connect(
        host='localhost',
        database='hospital',
        user='root',
        password='nepal2015'
    )
    if connection.is_connected():
        cursor = connection.cursor()
        fetch_query = """SELECT appointment_booked FROM doctors WHERE full_name = %s"""
        cursor.execute(fetch_query, (doctor_name,))
        result = cursor.fetchone()
        print(result)
        if result:
            current_appointments = result[0]
            new_appointments = current_appointments + 1
            update_query = """UPDATE doctors SET appointment_booked = %s WHERE full_name = %s"""
            cursor.execute(update_query, (new_appointments, doctor_name))
            connection.commit()
            query = """INSERT INTO patients (full_name, problem, doctor_booked, appointment_day) 
                    VALUES (%s, %s, %s, %s)"""
            cursor.execute(query, (patient_info['full_name'], patient_info['problem'], doctor_name, patient_info['appointment_day']))
            print(f"Appointment booked successfully for {doctor_name}")
            connection.commit()
        connection.close()

# Function to retrieve doctors' information from the database
def retrieve_database_info():
    connection = mysql.connector.connect(
        host='localhost',
        database='hospital',
        user='root',
        password='nepal2015'
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
    doctors_info = '\n'.join([str(doctor) for doctor in doctor_list])
    return doctors_info

doctors_info = retrieve_database_info()

# Initialize the chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a hospital's chatbot that answers questions from people wanting to book an appointment with a doctor. You have access to the hospital's doctor information to answer their questions."},
        {"role": "system", "content": f"Here is the doctor's information: {doctors_info}"},
        {"role": "system", "content": """
        If a user asks a normal question, respond with the relevant information and set 'schedule' to 'no'.
        If a user wants to book an appointment, ask for their full name, contact details, preferred appointment day, and the doctor they want to see. 
        Wrap this information in a dictionary format with keys: 'patient_info' and 'schedule', setting 'schedule' to 'yes'.
        Example for booking an appointment:
        {"patient_info": {"name": "John Doe", "contact": "123-456-7890", "preferred_day": "Monday", "doctor": "Dr. Smith"}, "schedule": "yes"}
        Example for normal questions:
        {"response": "Dr. Smith is available on Mondays and Wednesdays.", "schedule": "no"}
        """}
    ]

# Display chat messages excluding system messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

question = st.chat_input("How can I help you?")
if question:
    # Display user message to the container
    with st.chat_message("user"):
        st.markdown(question)

    # Add the message to the history
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        # Generate a response from the assistant
        generated = client.chat.completions.create(
            model="tiiuae/falcon-180b-chat",
            messages=[
                {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
            ],
            stream=False,
        )
        response = generated.choices[0].message.content
        
        try:
            response_dict = json.loads(response)  # Convert the response string to a dictionary
        except json.JSONDecodeError:
            response_dict = {"response": response, "schedule": "no"}

        if response_dict['schedule'] == 'no':
            st.markdown(response_dict['response'])

        elif response_dict['schedule'] == 'yes':
            patient_info = response_dict['patient_info']
            book_appointment(patient_info['doctor'], patient_info)
            st.markdown("Your appointment has been booked successfully.")

    # Add the assistant's response to the history
    st.session_state.messages.append({"role": "assistant", "content": response_dict['response']})
