import mysql.connector
from flask import Flask, request, jsonify
import json
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from datetime import datetime, timedelta

AI71_BASE_URL = "https://api.ai71.ai/v1/"
AI71_API_KEY = "api71-api-d1df6e20-b8cc-409c-af9f-3e6fe03de98e"

chat = ChatOpenAI(
    model="tiiuae/falcon-180B-chat",
    api_key=AI71_API_KEY,
    base_url=AI71_BASE_URL,
    streaming=True,
)

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="sayuj596",
        database="appointment_system"
    )
    return connection

def get_doctor_availability(doctor_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT availability FROM doctors WHERE id = %s", (doctor_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result['availability'] if result else None

def store_patient_request(patient_name, preferred_day, preferred_time, doctor_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO patients (name, preferred_day, preferred_time, doctor_id, appointment_timestamp) VALUES (%s, %s, %s, %s, NOW())",
        (patient_name, preferred_day, preferred_time, doctor_id)
    )
    connection.commit()
    cursor.close()
    connection.close()

def count_patients_in_slot(doctor_id, preferred_day, preferred_time):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = """
    SELECT COUNT(*) FROM patients
    WHERE doctor_id = %s AND preferred_day = %s AND preferred_time = %s
    """
    cursor.execute(query, (doctor_id, preferred_day, preferred_time))
    count = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return count

def schedule_appointment(patient_name, preferred_day, preferred_time, doctor_id=1):
    current_count = count_patients_in_slot(doctor_id, preferred_day, preferred_time)

    availability_json = get_doctor_availability(doctor_id)
    if not availability_json:
        return "No available slots for the requested doctor."

    doctor_availability = json.loads(availability_json)
    available_slots = doctor_availability.get(preferred_day, [])
    if not available_slots:
        return "No available slots for the requested day."

    prompt = (
        "You are a helpful assistant for scheduling appointments."
        f"Doctor's available slots on {preferred_day}: {', '.join(available_slots)}.\n"
        f"Patient's preferred time: {preferred_time}.\n"
        f"Current number of patients in this slot: {current_count}.\n"
        f"Currentcount:{current_count}\n"
        "Rule1 before making decision:Patient's preferred time block must exactly match in both starting and ending time any one of the doctors available slot\n"
    )

    response = chat.invoke(
        [
            SystemMessage(content=prompt),
            HumanMessage(content="is this appointment elligible to be scheduled according to the Rule 1 and Rule 2 both? Respond strictly in yes or no"),
        ]
    )

    # Ensure LLM respects the limit
    if  current_count<=10 and "yes" in response.content.lower():
        store_patient_request(patient_name, preferred_day, preferred_time, doctor_id)
        return "Appointment scheduled successfully."

    return "The appointment could not be scheduled."

app = Flask(__name__)

@app.route('/schedule_appointment', methods=['POST'])
def api_schedule_appointment():
    data = request.json
    patient_name = data.get("patient_name")
    preferred_day = data.get("preferred_day")
    preferred_time = data.get("preferred_time")
    doctor_id = data.get("doctor_id", 1)  # Default to doctor_id 1 if not provided

    response = schedule_appointment(patient_name, preferred_day, preferred_time, doctor_id)
    return jsonify({"confirmation": response})

if __name__ == '__main__':
    app.run(debug=True)
