import dotenv
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
import mysql.connector 
from mysql.connector import Error
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash')

def book_appointment(doctor_name,patient_info):
    connection = mysql.connector.connect(
        host='localhost',
        database='hospital',
        user='root',
        password='xxxxxxxx'
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
            query = """insert into patients (full_name,problem,doctor_booked,appointment_day) 
                    values (%s,%s,%s,%s)"""
          
            cursor.execute(query,(patient_info['full_name'],patient_info['problem'],doctor_name,patient_info['appointment_day']))
            print(f"Appointment booked successfully for {doctor_name}")
            connection.commit()
        connection.close()
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
if __name__ == "__main__":
      
        prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system","""You are a helpful assistant for answering questions of persons that are looking for booking an appointment to a doctor.
                you will be provided various information about doctors and you need to answer question using those informations.
                here is the doctors informations :
                {doctors_info}

                if the person says, he/she wants to have a appointment scheduled for specific doctor, ask them about their fullname,contact number and the appointment_day. and return it with a dictionary of them with a additional key appointment as yes.
                """
            ),
            (
                "human","{question}"
            )
        ]
    )
        chain = prompt | llm
        doctors_info = retrieve_database_info()

        question = input("How can I help you? ")
        
        response = chain.invoke(
            {
                'doctors_info': doctors_info,
                'question': question
            }
        )

        response_content = response.content
        print(response_content)