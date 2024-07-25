import google.generativeai as genai
import PIL.Image
import io
import os
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import streamlit as st

def report_to_record():
    # Load environment variables
    load_dotenv()

    # Configure API key for Gemini
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

    # Streamlit app title
    st.title("Report to Record")

    # Upload medical report image
    st.write("Input your report here !!! ")
    img_file = st.file_uploader(label="Report here")

    # Define the prompt for extracting data from the image
    prompt = ChatPromptTemplate.from_template(
        """
        You are an image-to-text converter. Your task is to convert medical report images into a dictionary of key-value pairs. The output should be in the following format:
        (key: value). (Example - Name: xyz)
        <context>
        {context}
        </context>
        Questions: {input}
        """
    )

    # Format the input for the model
    input_text = prompt.format(context="This is a medical report.", input="Extract information from this image")

    # Initialize the Gemini model
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    if img_file:
        # Convert UploadedFile to PIL.Image.Image
        img = PIL.Image.open(io.BytesIO(img_file.read()))

        # Generate the response using the image
        response = model.generate_content([input_text, img])

        # Extract the text from the response
        if response.candidates:
            text = response.candidates[0].content.parts[0].text

            # Replace curly braces with newlines for better formatting
            formatted_text = text.replace("{", "\n{").replace("}", "}\n")

            st.write(formatted_text)
        else:
            st.write("No content found.")
