import streamlit as st
from openai import OpenAI
import dotenv
import os
import json
import re
from PIL import Image
from audio_recorder_streamlit import audio_recorder
import base64
from io import BytesIO
import google.generativeai as genai
import random
from pymongo import MongoClient

# Function to find information by patient name
def find_information(patient_name):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Hospital']
    collection = db['Patients']
    patient_info = collection.find_one({"name": patient_name})
    print(patient_info)

# Function to store patient information in MongoDB
def information_store(patient_info):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Hospital']
    collection = db['Patients']
  
    if "name" not in patient_info:
        return
    else:
        collection.insert_one(patient_info)

dotenv.load_dotenv()

# Convert messages to a format for the Gemini model
def messages_to_gemini(messages):
    gemini_messages = []
    prev_role = None
    for message in messages:
        if prev_role and (prev_role == message["role"]):
            gemini_message = gemini_messages[-1]
        else:
            gemini_message = {
                "role": "model" if message["role"] == "assistant" else "user",
                "parts": [],
            }
        # Check if message["content"] is a list, if not, treat it as a single string
        if isinstance(message["content"], list):
            for content in message["content"]:
                if isinstance(content, dict):  # Ensure content is a dictionary
                    if content["type"] == "text":
                        gemini_message["parts"].append(content["text"])
                    elif content["type"] == "image_url":
                        gemini_message["parts"].append(base64_to_image(content["image_url"]["url"]))
                    elif content["type"] == "video_file":
                        gemini_message["parts"].append(genai.upload_file(content["video_file"]))
                    elif content["type"] == "audio_file":
                        gemini_message["parts"].append(genai.upload_file(content["audio_file"]))
        else:
            gemini_message["parts"].append(message["content"])

        if prev_role != message["role"]:
            gemini_messages.append(gemini_message)
        
        prev_role = message["role"]

    return gemini_messages

# Stream LLM response
def stream_llm_response():
    genai.configure()
    model = genai.GenerativeModel(
        model_name='gemini-1.5-pro',
        generation_config={
            "temperature": 0.3,
        }
    )
    gemini_messages = messages_to_gemini(st.session_state.messages)
    response = model.generate_content(contents=gemini_messages, stream=False)
    response = response.text
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        response_dict = json.loads(json_match.group())
        if response_dict['information_to_store'] != 'yes':
            response_message = response_dict["patient's response"]
            st.markdown(response_message)
        else:
            information_store(response_dict['information_to_store'])

        st.session_state.messages.append({
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": response_message,
                }
            ]
        })

# Helper function to convert file to base64
def get_image_base64(image_raw):
    buffered = BytesIO()
    image_raw.save(buffered, format=image_raw.format)
    img_byte = buffered.getvalue()
    return base64.b64encode(img_byte).decode('utf-8')

# Function to convert base64 string to image
def base64_to_image(base64_string):
    base64_string = base64_string.split(",")[1]
    return Image.open(BytesIO(base64.b64decode(base64_string)))

# Main function for the Streamlit app
def main():
    st.title("Additional Information")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "system",
                "content": """you are a hospital's agent responsible for extracting key information about
                the patients from communication with them or from the medical reports they provide so that whenever the doctor asks about the patient,
                you can answer using this information. You also answer patients' medical questions if they ask.
                
                The patient's information is to be stored in MongoDB, so it should be in a dictionary format with the main key being the patient's full name
                (you can ask during the conversation), and every other detail in a key-value pair.
                
                For each query, your response should contain two things:
                1. What you are going to answer the patient for his/her query.
                2. What information about him/her did you find.
                
                Your answer should always be in this following format:
                {"patient's response": "your answer to query", "information_to_store": "the patient's information"}
                
                The "information" key should be in this format only at the end of the conversation and should contain all patient details. 
                During the conversation, set information_to_store key to 'No'."""
            }
        ]

    # Display previous messages if there are any
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                for content in message["content"]:
                    if content["type"] == "text":
                        st.write(content["text"])
                    elif content["type"] == "image_url":
                        st.image(content["image_url"]["url"])
                    elif content["type"] == "audio_file":
                        st.audio(content["audio_file"])

    with st.sidebar:
        def reset_conversation():
            if "messages" in st.session_state and len(st.session_state.messages) > 0:
                st.session_state.pop("messages", None)

        st.button("🗑️ Reset conversation", on_click=reset_conversation)

        st.divider()

        st.write("### **🖼️ Add an image:**")

        def add_image_to_messages():
            if st.session_state.uploaded_img or st.session_state.camera_img:
                img_type = st.session_state.uploaded_img.type if st.session_state.uploaded_img else "image/jpeg"
                raw_img = Image.open(st.session_state.uploaded_img or st.session_state.camera_img)
                img = get_image_base64(raw_img)
                st.session_state.messages.append({
                    "role": "user",
                    "content": [{
                        "type": "image_url",
                        "image_url": {"url": f"data:{img_type};base64,{img}"}
                    }]
                })

        cols_img = st.columns(2)

        with cols_img[0]:
            with st.popover("📁 Upload"):
                st.file_uploader(
                    "Upload an image",
                    type=["png", "jpg", "jpeg"],
                    accept_multiple_files=False,
                    key="uploaded_img",
                    on_change=add_image_to_messages,
                )

        with cols_img[1]:
            with st.popover("📸 Camera"):
                activate_camera = st.checkbox("Activate camera")
                if activate_camera:
                    st.camera_input(
                        "Take a picture",
                        key="camera_img",
                        on_change=add_image_to_messages,
                    )

        # Audio Upload
        st.write("### **🎤 Add an audio:**")
        audio_prompt = None
        audio_file_added = False

        if "prev_speech_hash" not in st.session_state:
            st.session_state.prev_speech_hash = None

        speech_input = audio_recorder("Press to talk:", icon_size="3x", neutral_color="#6ca395")

        if speech_input and st.session_state.prev_speech_hash != hash(speech_input):
            st.session_state.prev_speech_hash = hash(speech_input)

            audio_id = random.randint(100000, 999999)
            with open(f"audio_{audio_id}.wav", "wb") as f:
                f.write(speech_input)

            st.session_state.messages.append({
                "role": "user",
                "content": [{
                    "type": "audio_file",
                    "audio_file": f"audio_{audio_id}.wav",
                }]
            })

            audio_file_added = True

    # Chat input
    if prompt := st.chat_input("Hi! Ask me anything...") or audio_prompt or audio_file_added:
        if not audio_file_added:
            st.session_state.messages.append({
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": prompt or audio_prompt,
                }]
            })

            # Display new message
            with st.chat_message("user"):
                st.markdown(prompt)
        else:
            # Display audio file
            with st.chat_message("user"):
                st.audio(f"audio_{audio_id}.wav")

        with st.chat_message("assistant"):
            stream_llm_response()

if __name__ == '__main__':
    main()
