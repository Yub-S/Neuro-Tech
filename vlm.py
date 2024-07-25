import os
from PIL import Image
import json
import pytesseract
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-pro", api_key=os.environ["GOOGLE_API_KEY"])

def extract_text_from_image(image):
    text = pytesseract.image_to_string(image)
    return text

def parse_text_to_dict(text):
    lines = text.split('\n')
    data = {"full_text": text}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip()
    return data

def solution(text):
    message = HumanMessage(content=f"According to this report provide a medical solution in a simple way:\n\n{text}")
    response = llm.invoke([message])
    return response

def main():
    st.title("Medical Report Analysis with Generative AI")
    st.write("""
    This app allows you to upload a medical report image, and then uses Generative AI to provide a medical solution based on the report.
    """)

    uploaded_file = st.file_uploader("Insert your medical report", type=["png", "jpg", "jpeg", "gif"])
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Medical Report', use_column_width=True)
        
        # Extract text from image
        with st.spinner('Extracting text from image...'):
            extracted_text = extract_text_from_image(image)

        if not extracted_text.startswith("Error:"):
            # Parse text to dictionary
            data_dict = parse_text_to_dict(extracted_text)
            st.write("Parsed Data:")
            st.json(data_dict)  # Optionally remove or comment this line if you don't want to display the parsed JSON data
            
            # Save dictionary as JSON file
            with open('data.json', 'w') as json_file:
                json.dump(data_dict, json_file)
            
            st.success("Data saved to data.json")
        
        if not extracted_text.startswith("Error:"):
            # Get medical solution
            with st.spinner('Generating medical solution...'):
                response = solution(extracted_text)
            
            st.write("Medical Solution:")
            st.write(response.content)

if __name__ == "__main__":
    main()
