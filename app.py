import streamlit as st
import google.generativeai as genai
import os
import requests
from dotenv import load_dotenv
from elevenlabs import ElevenLabs
from PIL import Image
import html

# -------------------- Streamlit Config & CSS --------------------
st.set_page_config(page_title="🤖 Electronics Assistant", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #dfe9f3 0%, #ffffff 100%);
            color: #1b1b1b;
            font-family: 'Poppins', sans-serif;
        }
        h1 {
            text-align:center;
            background: linear-gradient(90deg, #78ffd6, #a8edea);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size:2.5em;
            margin-bottom:20px;
        }
        .user-bubble {
            background: linear-gradient(135deg, #a1c4fd, #c2e9fb);
            color:#1b1b1b;
            padding:12px 16px;
            border-radius:18px;
            display:inline-block;
            margin:8px 0;
            box-shadow:0 2px 6px rgba(0,0,0,0.1);
            max-width:70%;
        }
        .tutor-bubble {
            background: linear-gradient(135deg, #fbc2eb, #a6c1ee);
            color:#1b1b1b;
            padding:12px 16px;
            border-radius:18px;
            display:inline-block;
            margin:8px 0;
            box-shadow:0 2px 6px rgba(0,0,0,0.1);
            max-width:70%;
        }
        input[type="text"], .stTextInput>div>input {
            width: 100% !important;
            border-radius:10px !important;
            border:1px solid #ccc !important;
            background: linear-gradient(135deg, #f0f4f8, #d9e2ec) !important;
            color:#1b1b1b !important;
            padding:10px !important;
            font-size: 1em !important;
        }
        div.stButton > button {
            background: linear-gradient(135deg, #89f7fe, #66a6ff);
            color:black;
            font-weight:600;
            border:none;
            border-radius:10px;
            padding:0.6em 1.2em;
            box-shadow:0 2px 6px rgba(0,0,0,0.15);
        }
        div.stButton > button:hover {
            background: linear-gradient(135deg, #66a6ff, #89f7fe);
            transform: scale(1.02);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>✨ Electronics & Robotics Chatbot ✨</h1>", unsafe_allow_html=True)

# -------------------- Load Environment --------------------
load_dotenv()
elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
gemini_key = "AIzaSyBd09L0gVBmuaTiJ-S3o5jZiuE4zd5892k"  # Replace with your valid Gemini API key
mouser_key = "a165ac49-3ade-43bd-aa1b-885cecae1f48"  # Replace or set in .env

# -------------------- Initialize Gemini --------------------
if not gemini_key:
    st.error("❌ GEMINI_API_KEY not found.")
else:
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    chat = model.start_chat()

# -------------------- Initialize ElevenLabs --------------------
client = ElevenLabs(api_key=elevenlabs_key) if elevenlabs_key else None

def text_to_speech(text, voice="Rachel"):
    if not client:
        return None
    try:
        audio = client.text_to_speech.convert(
            voice_id="21m00Tcm4TlvDq8ikWAM",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            text=text
        )
        return b"".join(audio)
    except Exception:
        return None

# -------------------- Tutor Prompt --------------------
tutor_system_prompt = """
You are a concise and friendly computer science tutor.
- Give answers in 3-4 short, clear sentences.
- Do NOT include code unless user says 'show code'.
- Suggest electronics parts (Arduino, ESP32, resistor) with description, image, price, and link (simulate Mouser).
- End each response with a thank you note.
"""

# -------------------- Mouser API Search --------------------
def search_mouser_parts(query, limit=3):
    if not mouser_key:
        return []
    url = f"https://api.mouser.com/api/v1/search/keyword?apiKey={mouser_key}"
    payload = {"SearchByKeywordRequest": {"keyword": query, "records": limit}}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        parts = []
        for item in data.get("SearchResults", {}).get("Parts", []):
            parts.append({
                "name": item.get("ManufacturerPartNumber", "Unknown"),
                "description": item.get("Description", "No description"),
                "link": item.get("ProductDetailUrl", "#"),
                "price": item.get("PriceBreaks", [{}])[0].get("Price", "N/A")
            })
        return parts
    except:
        return []

def display_mouser_parts(parts):
    for p in parts:
        st.markdown(f"""
        <div class="mouser-card">
            <a href="{p['link']}" target="_blank" style="font-weight:bold; text-decoration:none; color:#0000EE;">
                {p['name']}
            </a>
            <div>📦 {p['description']} | 💲 {p['price']}</div>
        </div>
        """, unsafe_allow_html=True)

# -------------------- Chat History --------------------
if "history" not in st.session_state:
    st.session_state.history = []

# -------------------- Image Upload --------------------
uploaded_file = st.file_uploader("📷 Upload an electronic component image", type=["png","jpg","jpeg"])
if uploaded_file:
    try:
        image = Image.open(uploaded_file)
        vision_prompt = "Identify the electronic component in this image. Respond only with the component name."
        response = model.generate_content([vision_prompt, image], stream=False)
        identified_component = response.text.strip()

        st.session_state.history.append({
            "user": "📷 Uploaded an image",
            "tutor": f"🔍 Gemini identified: **{identified_component}**"
        })

        # Mouser search
        products = search_mouser_parts(identified_component)
        if products:
            st.session_state.history.append({"user": None, "tutor": products})
        else:
            st.session_state.history.append({"user": None, "tutor": "⚠️ No matching parts found on Mouser."})

        # ElevenLabs TTS
        audio_data = text_to_speech(f"Identified: {identified_component}")
        if audio_data:
            st.session_state.history.append({"user": None, "audio": audio_data})

    except Exception as e:
        st.error(f"Image recognition error: {e}")

# -------------------- Text Chat --------------------
user_input = st.text_input("💡 Type your project idea or question:")
if st.button("Send") and user_input.strip():
    products = search_mouser_parts(user_input)
    mouser_text = products if products else []

    tutor_prompt = f"{tutor_system_prompt}\n\nUser project/question: {user_input}"
    try:
        response = chat.send_message(tutor_prompt, stream=True)
        output_text = "".join([chunk.text for chunk in response])
    except Exception as e:
        output_text = f"❌ Error: {e}"

    audio_data = text_to_speech(output_text)

    st.session_state.history.append({
        "user": user_input,
        "tutor": {"text": output_text, "products": mouser_text},
        "audio": audio_data
    })

# -------------------- Display Chat --------------------
for chat_pair in st.session_state.history:
    if chat_pair.get("user"):
        st.markdown(f"<div style='text-align:right; margin:10px;'><span class='user-bubble'>{html.escape(str(chat_pair['user']))}</span></div>", unsafe_allow_html=True)

    if chat_pair.get("tutor"):
        tutor_content = chat_pair["tutor"]
        if isinstance(tutor_content, list):
            display_mouser_parts(tutor_content)
        elif isinstance(tutor_content, str):
            st.markdown(f"<div style='text-align:left; margin:10px;'><span class='tutor-bubble'>{html.escape(tutor_content)}</span></div>", unsafe_allow_html=True)
        elif isinstance(tutor_content, dict):
            st.markdown(f"<div style='text-align:left; margin:10px;'><span class='tutor-bubble'>{html.escape(tutor_content.get('text',''))}</span></div>", unsafe_allow_html=True)
            if tutor_content.get("products"):
                display_mouser_parts(tutor_content["products"])
