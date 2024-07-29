from langchain.chat_models import ChatOpenAI
import streamlit as st
import os
from dotenv import load_dotenv
import uuid

load_dotenv()
from langchain.schema import HumanMessage, SystemMessage

AI71_BASE_URL = os.getenv("AI71_BASE_URL")
AI71_API_KEY = os.getenv("AI71_API_KEY")

chat = ChatOpenAI(
    model="tiiuae/falcon-180B-chat",
    api_key=AI71_API_KEY,
    base_url=AI71_BASE_URL,
    streaming=True,
)

# Initialize session state for conversation history and user data
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_history' not in st.session_state:
    st.session_state.user_history = {}
if 'health_conditions' not in st.session_state:
    st.session_state.health_conditions = {}
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if 'asked_for_health_info' not in st.session_state:
    st.session_state.asked_for_health_info = False

def save_user_data(user_id, data):
    st.session_state.user_history[user_id] = data

def load_user_data(user_id):
    return st.session_state.user_history.get(user_id, None)

def ask_health_conditions():
    return (
        "Let's understand your health conditions first. Please provide the following details:\n"
        "- Age\n"
        "- Weight (kg)\n"
        "- Height (cm)\n"
        "- Activity Level (Low, Moderate, High)"
    )

def generate_prompt(health_conditions):
    return (
        f"Based on the following health conditions: {health_conditions}, "
        "provide general meal planning advice. Note that this is not a substitute for professional dietary guidance. "
        "Suggestions should be practical and based on commonly known dietary principles."
    )

def get_meal_plan(prompt):
    response = ""
    try:
        for chunk in chat.stream(prompt):
            response += chunk.content
    except Exception as e:
        st.error(f"Error getting meal plan: {e}")
    return response

st.header("AI Meal and Diet Planner")

# Check if user data exists
user_data = load_user_data(st.session_state.user_id)
if user_data:
    st.write("Welcome back! Let's continue where we left off.")
    st.write(f"Previous health data: {user_data}")
    st.session_state.health_conditions = user_data
else:
    if not st.session_state.asked_for_health_info:
        st.session_state.messages.append({"role": "assistant", "content": ask_health_conditions()})
        st.session_state.asked_for_health_info = True

# Display all messages from chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input prompt for user message
prompt = st.chat_input("Type your message here")

if prompt:
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Append user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    if not st.session_state.health_conditions:
        # Parse health conditions from user message
        try:
            # Validate and parse input
            parts = prompt.split()
            if len(parts) == 4 and all('=' in part for part in parts):
                age, weight, height, activity_level = [part.split('=')[1].strip() for part in parts]
                st.session_state.health_conditions = {
                    "Age": age,
                    "Weight": weight,
                    "Height": height,
                    "Activity Level": activity_level
                }
                save_user_data(st.session_state.user_id, st.session_state.health_conditions)
                meal_prompt = generate_prompt(st.session_state.health_conditions)
                meal_plan = get_meal_plan(meal_prompt)
                response = f"Here is some general meal planning advice based on your health conditions:\n{meal_plan}"
            else:
                response = "Please provide your health details in the format: age=XX weight=XX height=XX activity level=XX"
        except ValueError:
            response = "Please provide your health details in the format: age=XX weight=XX height=XX activity level=XX"
    else:
        # Continue the conversation with chat history
        chat_history = "\n".join([msg["content"] for msg in st.session_state.messages])
        response = get_meal_plan(f"Continue the conversation with the following history:\n{chat_history}\nUser: {prompt}")
    
    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Append assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
