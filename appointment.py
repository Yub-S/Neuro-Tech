import dotenv
import os
import openai
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import mysql.connector 
from mysql.connector import Error
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

load_dotenv()
# api_key = os.getenv('GOOGLE_API_KEY')
api_key = os.getenv('AI71_API_KEY')
llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash')
AI71_BASE_URL = "https://api.ai71.ai/v1/"

chat = ChatOpenAI(
    model="tiiuae/falcon-180B-chat",
    api_key=api_key,
    base_url=AI71_BASE_URL,
    streaming=True,
)

api_key = os.getenv('AI71_API_KEY')
client = openai.OpenAI(api_key=api_key,base_url=AI71_BASE_URL)

def book_appointment(doctor_name,patient_info):
    connection = mysql.connector.connect(
        host='localhost',
        database='hospital',
        user='root',
        password='xxxxxxx'
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
        password='xxxxxxx'
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
      
        doctors_info = retrieve_database_info()

        question = input("How can I help you? ")
        
        template1 = ("""You are a helpful assistant for answering questions of persons that are looking for booking an appointment to a doctor.
            you will be provided various information about doctors and you need to answer question using those informations.return your answer as a json with key being answer.
            here is the doctors informations :
            {doctors_info}
                  
            if the user confirms to schedule the meeting with a doctor, ask his/her fullname,contact_details,appointment_time,doctor's name. and send it as a json.      """
        )

        prompt1 = PromptTemplate(template=template1,input_variables=["doctor_info","question"])

        chain1 = prompt1 | chat | JsonOutputParser()

        response1 = chain1.invoke(
             [doctors_info,question]
         )

        template2 = ("""you are a response checker that checks whether the reponse from the previous model has a personal information of a person mainly: fullname,contact no, doctors name and a appointment_day.
                    if it does contain that reply Yes as a josn with key schedule_appointment . else reply No.
                    here is the response :
                    {response} """)
        
        prompt2 = PromptTemplate(template=template2,input_variables=['response'])

        chain2 = prompt2 | chat | JsonOutputParser()
        response2 = chain2.invoke([response1['answer']])
        print(response2)