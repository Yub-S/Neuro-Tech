import openai
import os
from dotenv import load_dotenv
import streamlit as st
import mysql.connector
import json
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Load environment variables
load_dotenv()
AI71_BASE_URL = "https://api.ai71.ai/v1/"

api_key = os.getenv('AI71_API_KEY')
client = openai.OpenAI(api_key=api_key, base_url=AI71_BASE_URL)

st.title("MediSched")

def send_emails(patient_email, text_to_send):
    try:
        # Email server setup
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        # Login credentials (use environment variables for security)
        sender_email = os.getenv('email')
        sender_password = os.getenv('password')
        server.login(sender_email, sender_password)

        # Compose the email
        subject = "Confirmation mail"
        body = f"{text_to_send}"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = patient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        server.send_message(msg)
        print("Mail sent")


    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        # Close the server connection
        server.quit()


#Book appointment function
def book_appointment(patient_info):
    connection = mysql.connector.connect(
    host='localhost',
    database='hospital',
    user='root',
    password=os.getenv('mysql_password')
)
    
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
            st.markdown("The selected time slot on {} at {} is already booked. Please choose another time slot.".format(preferred_day, preferred_time))
            st.session_state.messages.append({"role":"assistant","content":"The selected time slot is already booked. Please choose another time slot."})
        else:
            # The time slot is available, proceed with booking
            insert_query = """INSERT INTO patients (full_name, problem,email, doctor_booked, appointment_day, appointment_time) 
                              VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(insert_query, (
                patient_info['name'], 
                patient_info['problem'], 
                patient_info['email'], 
                doctor_name, 
                preferred_day, 
                preferred_time
            ))
            connection.commit()

            conformation_text="Appointment booked successfully for {} on {} at {}.".format(patient_info['name'], preferred_day, preferred_time)
            # st.markdown(marking)
            send_emails(patient_info['email'],conformation_text) 

        connection.close()

def reschedule_appointment(new_info):
    connection = mysql.connector.connect(
    host='localhost',
    database='hospital',
    user='root',
    password=os.getenv('mysql_password')
)
    
    if connection.is_connected():
        cursor = connection.cursor()

        # Fetch the current appointment details
        fetch_query = """SELECT email,doctor_booked, appointment_day, appointment_time 
                         FROM patients WHERE full_name = %s"""
        cursor.execute(fetch_query, (new_info['name'],))
        result = cursor.fetchone()
        
        if result:
            email,doctor_name, current_day, current_time = result

            # Check if the new day and time slot are already booked for the same doctor
            check_query = """SELECT * FROM patients 
                             WHERE doctor_booked = %s AND appointment_day = %s AND appointment_time = %s"""
            cursor.execute(check_query, (doctor_name, new_info['new_day'], new_info['new_time']))
            check_result = cursor.fetchone()

            if check_result:
                # New time slot is already booked
                st.markdown("The selected new time slot on {} at {} is already booked. Please choose another time slot.".format(new_info['new_day'], new_info['new_time']))
                st.session_state.messages.append({"role":"assistant","content":"The selected time slot is already booked. Please choose another time slot."})
            else:
                # The new time slot is available, proceed with rescheduling
                update_patient_query = """UPDATE patients 
                                          SET appointment_day = %s, appointment_time = %s 
                                          WHERE full_name = %s"""
                cursor.execute(update_patient_query, (new_info['new_day'], new_info['new_time'], new_info['name']))
                connection.commit()

                confirmation_text="Appointment rescheduled successfully to {} on {}.".format(new_info['new_time'], new_info['new_day'])
                send_emails(email,confirmation_text)
                
        else:
            st.markdown("Patient not found.")

        connection.close()

          
def cancel_appointment(patient_name):
    connection = mysql.connector.connect(
        host='localhost',
        database='hospital',
        user='root',
        password=os.getenv('mysql_password')
    )

    if connection.is_connected():
        cursor = connection.cursor()

        # Fetch the current appointment details for the patient
        fetch_query = """SELECT email,doctor_booked, appointment_day, appointment_time 
                         FROM patients WHERE full_name = %s"""
        cursor.execute(fetch_query, (patient_name,))
        result = cursor.fetchone()
        
        if result:
            email,doctor_name, appointment_day, appointment_time = result

            # Remove the patient's appointment from the patients table
            delete_patient_query = """DELETE FROM patients WHERE full_name = %s"""
            cursor.execute(delete_patient_query, (patient_name,))
            
            # Commit the changes
            connection.commit()

            confirmation_text = f"Appointment with {doctor_name} on {appointment_day} at {appointment_time} canceled successfully."
            send_emails(email,confirmation_text)
        else:
            st.markdown("Patient not found.")
        
        connection.close()

# Function to retrieve doctors' information from the database
def retrieve_database_info():
    connection = mysql.connector.connect(
    host='localhost',
    database='hospital',
    user='root',
    password=os.getenv('mysql_password')
)
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

doctors_info = retrieve_database_info()

#Initialize the chat history

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a hospital's chatbot that helps people book, reschedule, or cancel appointments with doctors. You have access to the hospital's doctor information."},
        {"role": "system", "content": f"Here is the doctor's information: {doctors_info}"},
        {"role": "system", "content": """
Instructions:

1. **Conversational Questions:**
   - Reply freely but use the following format:
     ```
     {"response": "your reply", "schedule": "no"}
     ```

2. **Doctor Information:**
   - If asked about a doctor, respond with relevant details and use this format:
     ```
     {"response": "Dr. Alice Smith is available from Monday to Friday at 11:00 AM-12:00 AM and 2:00 PM-3:00 PM.", "schedule": "no"}
     ```
   - Recommend doctors based on the user's problem (e.g., cardiologist for heart issues).

3. **Book an Appointment:**
   - Ask for: full name, problem, preferred day, preferred time, email, and doctor if not provided earlier.
   - If all details are provided, format the response like this:
     ```
     {"response": "Your appointment has been scheduled with Dr. Smith for Monday at 2:00 PM. You will receive a confirmation email soon.", 
     "patient_info": {"name": "John Doe", "problem": "Headache", "preferred_day": "Monday", "preferred_time": "2:00 PM-3:00 PM", "email": "JohnDoe@gmail.com", "doctor": "Dr. Smith"}, 
     "schedule": "yes"}
     ```

4. **Reschedule an Appointment:**
   - Ask for: full name, new day, new time if not provided earlier.
   - If all details are provided, format the response like this:
     ```
     {"response": "Your appointment has been rescheduled for Tuesday at 11:00 AM. You will receive a confirmation email soon.", 
     "new_info": {"name": "John Doe", "new_day": "Tuesday", "new_time": "11:00 AM - 12:00 PM"}, 
     "schedule": "reschedule"}
     ```

5. **Cancel an Appointment:**
   - Ask for: full name.
   - If the name is provided, format the response like this:
     ```
     {"response": "Your appointment with Dr. Smith has been cancelled. You will receive a confirmation email soon.", 
     "patient_name": "John Doe", 
     "schedule": "cancel"}
     ```

- Note that, there are book_appointment,reschedule_appointment and cancel_appointment functions defined to do the appointment,rescheduling and cancellation job. you just need to respond in the corresponding format as shown above to trigger these functions.        
        """}
    ]

# Display chat messages excluding system messages
for message in st.session_state.messages:
    if message["role"] != "system":
        if message["role"] == "assistant":
            try:
                json_objects = message["content"].splitlines()
                for json_str in json_objects:
                    if json_str.strip():  
                        response_content_prev = json.loads(json_str)
                        with st.chat_message(message["role"]):
                            st.markdown(response_content_prev["response"])
            except json.JSONDecodeError as e:
                print(f"JSON decoding error: {e}")
        else:
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
        response_content = generated.choices[0].message.content
        # st.markdown(response_content)
        try:
            # Extract JSON from the response content
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                response_dict = json.loads(json_match.group())
                if response_dict['schedule'] == 'no':
                    st.markdown(response_dict['response'])

                elif response_dict['schedule'] == 'yes':
                    patient_info = response_dict['patient_info']
                    book_appointment(patient_info)
                    st.markdown(response_dict['response'])

                elif response_dict['schedule']=='reschedule':
                    new_info = response_dict['new_info']
                    reschedule_appointment(new_info)
                    st.markdown(response_dict['response'])

                elif response_dict['schedule']=='cancel':
                    patient_name=response_dict['patient_name']
                    cancel_appointment(patient_name)
                    st.markdown(response_dict['response'])
            else:
                st.error("No valid JSON found in the response.")
        except json.JSONDecodeError:
            st.error("Failed to parse response as JSON.")
    # Add the assistant's response to the history
    st.session_state.messages.append({"role": "assistant", "content": response_content})