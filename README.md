# Medi-Sched
### Contents:
- [Introduction](https://github.com/Yub-S/Neuro-tech?tab=readme-ov-file#introduction)
- [Major features](https://github.com/Yub-S/Neuro-tech?tab=readme-ov-file#majorfeatures)
- [How Medi-Sched works?](https://github.com/Yub-S/Neuro-tech?tab=readme-ov-file#howmedi-schedworks?)

### Introduction
 MediShed is an intelligent chatbot application designed to streamline the process of booking, rescheduling, and canceling patient appointments with doctors. By leveraging Falcon LLM, MediShed provides a user-friendly interface that efficiently handles patient inquiries and appointment management. This reduces administrative burdens on hospital staff and enhances the overall patient experience. With features like real-time doctor information retrieval, automated email confirmations, and robust error handling, MediShed ensures seamless and accurate appointment scheduling.
### Major Features
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

### How Medi-Sched works?
