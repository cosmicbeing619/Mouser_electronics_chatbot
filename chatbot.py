import os
import google.generativeai as genai
from dotenv import load_dotenv

import re

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html)

# Then inside your loop:
for chunk in response:
    text = clean_html(chunk.text)
    print(text, end="", flush=True)
    output_text += text


# -------------------------
# Load Environment Variables
# -------------------------
load_dotenv()
api_key = "AIzaSyBd09L0gVBmuaTiJ-S3o5jZiuE4zd5892k"
if not api_key:
    print("Error! GEMINI_API_KEY not found in environment.")
    exit()

genai.configure(api_key=api_key)

# -------------------------
# Configure Tutor Chatbot
# -------------------------
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat()

# Tighter instructions for short answers
tutor_system_prompt = """
You are a concise and friendly computer science tutor.
- Give answers in 3-4 short, clear sentences.
- Do NOT include code unless the user explicitly says 'show code' or 'example code'.
- Give one link of site with codes related to the product. 
- If user asks for an electronics part (keywords like 'Arduino', 'ESP32', 'resistor'), 
  respond with a short description and display product image, price, and link (simulate Mouser API).
- End each response with a thank you note.
"""

print("CS Tutor Chatbot (Gemini 2.0 Flash) is ready!")
print("Type 'quit' to exit.")
print("=" * 50)

history = []

while True:
    user_input = input("\nYou: ").strip()
    if not user_input:
        print("Please type something for the tutor to respond.")
        continue
    if user_input.lower() == "quit":
        print("\nGoodbye! Keep learning and practicing. 👨‍💻")
        break

    tutor_prompt = f"{tutor_system_prompt}\n\nUser: {user_input}"

    try:
        response = chat.send_message(tutor_prompt, stream=True)
        output_text = ""
        print("\nTutor: ", end="")
        for chunk in response:
            print(chunk.text, end="", flush=True)
            output_text += chunk.text
        print("\n" + "-" * 50)

        history.append({"user": user_input, "tutor": output_text})
    except Exception as e:
        print(f"Error while getting response from Gemini: {e}")
