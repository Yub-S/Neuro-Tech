# Medi-Sched
### Contents:
- [Introduction](https://github.com/Yub-S/Neuro-tech?tab=readme-ov-file#introduction)
- [Major Highlights](https://github.com/Yub-S/Neuro-tech?tab=readme-ov-file#major-highlights)
- [How Medi-Sched works?](https://github.com/Yub-S/Neuro-tech?tab=readme-ov-file#how-medisched-works)
- [How to run locally?](https://github.com/Yub-S/Neuro-tech?tab=readme-ov-file#how-to-run-locally)


### Introduction
 MediShed is an intelligent chatbot application designed to streamline the process of booking, rescheduling, and canceling patient appointments with doctors. By leveraging Falcon LLM, MediShed provides a user-friendly interface that efficiently handles patient inquiries and appointment management. This reduces administrative burdens on hospital staff and enhances the overall patient experience. With features like real-time doctor information retrieval, automated email confirmations, and robust error handling, MediShed ensures seamless and accurate appointment scheduling.
### Major Highlights
### Doctor Information Retrieval
- **Comprehensive Database Access:** Retrieves and presents detailed information about doctors, including their availability and specialties, from a MySQL database.
- **Specialty Recommendations:** Suggests doctors based on the patient's specific problem or condition, ensuring they receive the most appropriate care.

### Appointment Booking
- **User-Friendly Booking Process:** Allows patients to book appointments by providing their full name, the problem they're experiencing, their preferred appointment day and time, contact email, and the doctor they want to visit.
- **Availability Check:** Verifies doctor availability in real-time to prevent double bookings.
- **Confirmation Emails:** Automatically sends appointment confirmation emails to patients, ensuring they have all necessary details.

### Appointment Rescheduling
- **Easy Rescheduling:** Patients can reschedule their appointments by providing their full name, new preferred appointment day, and time.
- **Conflict Management:** Checks the availability of the new time slot and updates the appointment details in the database.
- **Reschedule Confirmation:** Sends confirmation emails to patients after successfully rescheduling their appointments.

### Appointment Cancellation
- **Simple Cancellation Process:** Patients can cancel their appointments by providing their full name.
- **Database Update:** Removes the appointment from the database.
- **Cancellation Emails:** Sends cancellation confirmation emails to patients, ensuring they are informed of the cancellation.

### Conversational Interface
- **Natural Language Processing:** Utilizes the Falcon LLM to handle conversational queries and generate human-like responses.
- **Structured Responses:** Provides responses in a structured dictionary format, making it easy to trigger appropriate actions (e.g., booking, rescheduling, or canceling appointments).

### Technical Excellence
- **Robust Backend:** Built with Python for backend logic, ensuring efficient integration with the database and email services.
- **Interactive Frontend:** Uses Streamlit to create an interactive and user-friendly web interface for the chatbot.
- **Secure Email Service:** Utilizes SMTP for sending confirmation and cancellation emails, ensuring patient communication is handled securely.

### Error Handling and Security
- **Real-Time Synchronization:** Ensures real-time updates of doctor availability and appointment statuses, improving coordination and reducing errors.
- **Error Management:** Handles potential issues gracefully, providing clear feedback to users.
- **Data Privacy:** Adheres to healthcare regulations, ensuring the privacy and security of patient information during all communications and database operations.

### How MediSched works?
- Doctor's information is fed from the database to Falcon LLM.
- The LLM converses with the user to gather necessary input.
- Upon receiving the required information, the LLM generates a response in dictionary format.
- The response is converted to JSON to extract the needed keys.
- The extracted keys trigger one of three functions based on user request:
  - `book_appointment`
  - `reschedule_appointment`
  - `cancel_appointment`
- Each of these functions triggers the `send_emails` function to send a confirmation to the user.
### How to run locally?
On the project folder:


> ```pip install -r requirements.txt```
###.env file must be in this format:
###> ```AI71_API_KEY="api_key_of_falcon_llm"```
###> ```mysql_password="your_sql_password_here"```
###> ```email="your_email_with_app_password"```
###> ```password="your_16_character_long_password"```
