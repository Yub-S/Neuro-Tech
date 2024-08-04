import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, FewShotChatMessagePromptTemplate
import mysql.connector
import json
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from datetime import datetime

# Get the current date and time
now = datetime.now()

# Format the day of the week and the full date
day_of_week = now.strftime("%A")
full_date = now.strftime("%Y-%m-%d")

# Set up the OpenAI model
AI71_BASE_URL = "https://api.ai71.ai/v1/"
AI71_API_KEY1 = "api71-api-d1df6e20-b8cc-409c-af9f-3e6fe03de98e"
AI71_API_KEY2="ai71-api-d2163647-7b39-4545-b47e-1202c2aeaad9"

chat = ChatOpenAI(
    model="tiiuae/falcon-180B-chat",
    api_key=AI71_API_KEY1,
    base_url=AI71_BASE_URL,
    streaming=True,
)
chat1 = ChatOpenAI(
    model="tiiuae/falcon-180B-chat",
    api_key=AI71_API_KEY2,
    base_url=AI71_BASE_URL,
    streaming=True,
)
AI71_API_KEY3="ai71-api-0a056558-f068-4374-914a-6e2f0f1bb564"
chat2 = ChatOpenAI(
    model="tiiuae/falcon-180B-chat",
    api_key=AI71_API_KEY3,
    base_url=AI71_BASE_URL,
    streaming=True,
)
# Define the example prompts
examples = [
    {"input": "Hey I am having a stomach ache, is any specialized doctor available?", "output": "Yes, a doctor with name John is available on Monday in slots of [12:00-1:00]. Would you like to book an appointment?"},
    {"input": "Can you book an appointment with this doctor on Tuesday?", "output": "No, the doctor is not available on that day. He is available on..."},
    {"input": "Can you book an appointment with this doctor between 4 and 6 pm?", "output": "No, the doctor is not available in that time block. He is available on time blocks:..."},
]

example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
)

# Read doctors info from the database
def read_doctors_table():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="sayuj596",  # Replace with your database password
        database="appointment_system"
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()
    cursor.close()
    connection.close()

    doctors_info = "Here are the available doctors and their schedules:\n"
    for doctor in doctors:
        availability = json.loads(doctor['availability'])
        availability_str = ", ".join([f"{day}: {', '.join(times)}" for day, times in availability.items()])
        doctor_info = f"ID: {doctor['id']}, Name: {doctor['name']}, Speciality: {doctor['speciality']}, Availability: {availability_str}\n"
        doctors_info += doctor_info

    return doctors_info

# Streamlit app
st.title("Chatbot Interface")

# Initialize session state if it doesn't exist
if 'messages' not in st.session_state:
    st.session_state.messages = []

doctors_info = read_doctors_table()

# Integrate the message assistant form and input field together
with st.form(key='chat_form'):
    user_input = st.text_input("You:", "")
    submit_button = st.form_submit_button(label="Message Assistant")

    if submit_button and user_input:
        st.session_state.messages.append({'role': 'user', 'content': user_input})

        # Get doctor's information

        # Construct chat history
        chat_history = ""
        for message in st.session_state.messages:
            if message['role'] == 'user':
                chat_history += f"User: {message['content']}\n"
            else:
                chat_history += f"Bot: {message['content']}\n"

        # Generate response from the chatbot
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system", """You are a highly skilled appointment scheduler of a hospital that helps patients to find the right doctor by 
                    understanding the symptoms and suggesting a specialized doctor that is more likely to cure that symptom.\n
                    The day of week today is {day_of_week}
                    The date today is {full_date}
                    Here is the information about available doctors:
                    {doctors_info}
                    """),(
                    "system","""
                    Conversation so far:
                    {chat_history}"""),
                    ("system","""
                    If the person says a time then if the time falls under any of the available time block of the doctor then only move forward the scheduling process
                    else say on that time doctor is not available and give the doctors available time block for that day

                    If the person says, he/she wants to have an appointment scheduled, then ask them about their full name, contact number, and the appointment day
                    if (the user provides his/her information) and (the day and time block have been fixed), say thank you the appointment has been scheduled.
                    After getting all the information please ensure the user to click confirmation button to submit the appointment
                    """
                ),
                
                ("human", "{input}"),
            ]
        )

        chain = prompt | chat
        response = chain.invoke(
            {
                'doctors_info': doctors_info,
                'day_of_week': day_of_week,
                'full_date':full_date,
                'chat_history': chat_history,
                'input': user_input
            }
        )
        response_content = response.content

        st.session_state.messages.append({'role': 'bot', 'content': response_content})

# Display the chat messages with icons
for message in st.session_state.messages:
    if message['role'] == 'user':
        st.markdown(f"""
        <div style="display: flex; align-items: center;">
            <img src="https://img.icons8.com/ios-filled/50/ffffff/user.png" width="30" style="margin-right: 10px;">
            <p>{message['content']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display: flex; align-items: center;">
            <img src="https://img.icons8.com/ios-filled/50/ffffff/robot.png" width="30" style="margin-right: 10px;">
            <p>{message['content']}</p>
        </div>
        """, unsafe_allow_html=True)

def insert_patient_info(patient_info):
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="sayuj596",  # Replace with your database password
            database="appointment_system"
        )
        cursor = connection.cursor()

        # Prepare the SQL query
        sql_query = """
        INSERT INTO patients (doctor_name, full_name, contact_number, appointment_day, appointment_block)
        VALUES (%s,%s, %s, %s, %s)
        """
        data = (
            patient_info['doctor_name'],
            patient_info['FullName'],
            patient_info['ContactInfo'],
            patient_info['AppointmentDay'],
            patient_info['AppointmentBlock']
        )

        # Execute the query
        cursor.execute(sql_query, data)
        connection.commit()

        # Output the result
        print(f"Patient information inserted with ID: {cursor.lastrowid}")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def extract_user_messages(messages):
    all_messages = ""
    for message in messages:
            all_messages += message['content'] + " "
    return all_messages.strip()

# Define data model for extracting patient information
class PatientInfo(BaseModel):
    FullName: str = Field(description="The full name of the patient from the patient message")
    ContactInfo: str = Field(description="The contact information of the patient from the patient message")
    AppointmentDay: str = Field(description="The appointment day of the patient from the patient message")
    AppointmentBlock: str = Field(description="The appointment block of the patient from the patient message")
    doctor_name: str = Field(description="The name of the doctor that the patient chooses")

parser = JsonOutputParser(pydantic_object=PatientInfo)

# Define the prompt for extracting patient information
prompt1 = PromptTemplate(
    template="You are a skilled extractor of patient information from the given text.\nYou strictly must not take part in user conversations.\nif the information about the patient is not in the conversation yet wait for few second\n{format_instructions}\n{patient_message}\n",
    input_variables=["patient_message"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# Extract patient information from user messages
chain1 = prompt1 | chat2 | parser
# Button for booking appointment
if st.button("Confirm Appointment"):
    st.write("User messages saved for appointment booking.")
    patient_info = chain1.invoke({"patient_message": str(message)})
    insert_patient_info(patient_info)
