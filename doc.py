from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# Sample data for doctors
doctors = [
    {
        "name": "Dr. John Smith",
        "specialization": "Cardiologist",
        "shift": "9 AM - 5 PM",
        "contact": "555-1234"
    },
    {
        "name": "Dr. Jane Doe",
        "specialization": "Neurologist",
        "shift": "10 AM - 6 PM",
        "contact": "555-5678"
    },
    {
        "name": "Dr. Emily Clark",
        "specialization": "Pediatrician",
        "shift": "8 AM - 4 PM",
        "contact": "555-8765"
    }
]

def generate_pdf(file_name, doctors):
    c = canvas.Canvas(file_name, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1 * inch, height - 1 * inch, "Hospital Doctor Records")

    # Set up for doctor records
    c.setFont("Helvetica", 12)
    y_position = height - 1.5 * inch

    for doctor in doctors:
        c.drawString(1 * inch, y_position, f"Name: {doctor['name']}")
        y_position -= 0.4 * inch
        c.drawString(1 * inch, y_position, f"Specialization: {doctor['specialization']}")
        y_position -= 0.4 * inch
        c.drawString(1 * inch, y_position, f"Shift: {doctor['shift']}")
        y_position -= 0.4 * inch
        c.drawString(1 * inch, y_position, f"Contact: {doctor['contact']}")
        y_position -= 0.6 * inch

        # Add a line to separate records
        c.line(0.5 * inch, y_position + 0.1 * inch, width - 0.5 * inch, y_position + 0.1 * inch)
        y_position -= 0.4 * inch

    c.save()

# Generate PDF with doctor records
generate_pdf("doctors_records.pdf", doctors)
