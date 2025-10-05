import streamlit as st
import google.generativeai as genai
import os
import requests
from elevenlabs import ElevenLabs
from PIL import Image
import re
import html
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# -------------------- Helper Function --------------------
def clean_html(raw_html):
    """Remove HTML tags and stray closing tags from LLM or API output."""
    try:
        soup = BeautifulSoup(raw_html, "html.parser")
        clean_text = soup.get_text(separator=" ", strip=True)
    except Exception:
        clean_text = raw_html
    clean_text = re.sub(r'</?[^>]+>', '', clean_text)
    clean_text = clean_text.replace('</span>', '').replace('</div>', '')
    return clean_text.strip()

# -------------------- Initialize ElevenLabs --------------------
elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
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

# -------------------- Streamlit Config --------------------
st.set_page_config(page_title="🤖 Electronics Parts Finder", page_icon="🔌", layout="wide")

# -------------------- CSS Styling --------------------
st.markdown("""
    <style>
        body {background: linear-gradient(135deg, #dfe9f3 0%, #ffffff 100%); color: #1b1b1b; font-family: 'Poppins', sans-serif;}
        h1 {text-align:center; background: linear-gradient(90deg, #78ffd6, #a8edea); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size:2.5em; margin-bottom:20px;}
        .user-bubble {background: linear-gradient(135deg, #a1c4fd, #c2e9fb); color:#1b1b1b; padding:12px 16px; border-radius:18px; display:inline-block; margin:8px 0; box-shadow:0 2px 6px rgba(0,0,0,0.1);}
        .tutor-bubble {background: linear-gradient(135deg, #fbc2eb, #a6c1ee); color:#1b1b1b; padding:12px 16px; border-radius:18px; display:inline-block; margin:8px 0; box-shadow:0 2px 6px rgba(0,0,0,0.1);}
        input[type="text"] {border-radius:10px !important; border:1px solid #ccc !important; background-color:#f9fbfd !important; color:#333 !important;}
        div.stButton > button {background: linear-gradient(135deg, #89f7fe, #66a6ff); color:black; font-weight:600; border:none; border-radius:10px; padding:0.6em 1.2em; box-shadow:0 2px 6px rgba(0,0,0,0.15);}
        div.stButton > button:hover {background: linear-gradient(135deg, #66a6ff, #89f7fe); transform: scale(1.02);}
        .mouser-card {display:flex; align-items:center; gap:10px; border-radius:12px; padding:10px; margin:5px 0; background:#f9f9f9; box-shadow:0 2px 8px rgba(0,0,0,0.1);}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>✨ Electronics & Robotics Chatbot ✨</h1>", unsafe_allow_html=True)

# -------------------- Configure Gemini --------------------
load_dotenv()
gemini_key = "AIzaSyBd09L0gVBmuaTiJ-S3o5jZiuE4zd5892k"
mouser_key = os.getenv("MOUSER_API_KEY")

if not gemini_key:
    st.error("❌ GEMINI_API_KEY not found. Please add it to .env or Streamlit secrets.")
else:
    genai.configure(api_key=gemini_key)

model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat()

tutor_system_prompt = """
You are a concise and friendly computer science tutor.
- Give answers in 3-4 short, clear sentences.
- Do NOT include code unless the user explicitly says 'show code' or 'example code'.
- Suggest electronics parts if user asks for Arduino, ESP32, resistors, sensors, etc.
- End each response with a thank you note.
"""

# -------------------- Mouser API Search --------------------
def search_mouser(keyword: str, limit: int = 5):
    """Search Mouser for parts by keyword and return product name + link."""
    if not mouser_key:
        st.error("⚠️ Mouser API key not found.")
        return []

    url = f"https://api.mouser.com/api/v1/search/keyword?apiKey={mouser_key}"
    payload = {
        "SearchByKeywordRequest": {
            "keyword": keyword,
            "records": limit
        }
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        results = data.get("SearchResults", {}).get("Parts", [])
        parts_list = []
        for part in results:
            name = part.get("ManufacturerPartNumber") or part.get("MouserPartNumber") or "Unknown Part"
            url = part.get("ProductDetailUrl", "#")
            parts_list.append({"name": name, "url": url})
        return parts_list
    except Exception as e:
        st.error(f"⚠️ Mouser API error: {e}")
        return []

def display_mouser_products(products):
    for p in products:
        st.markdown(f"""
        <div class="mouser-card">
            <a href="{p['url']}" target="_blank" style="font-weight:bold; text-decoration:none; color:#0000EE;">
                {p['name']}
            </a>
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
        # Gemini identifies the component
        vision_prompt = "Identify the electronic component in this image. Respond only with the component name."
        response = model.generate_content([vision_prompt, image], stream=False)
        identified_component = clean_html(response.text.strip())

        st.session_state.history.append({
            "user":"📷 Uploaded an image",
            "tutor":f"🔍 Gemini identified: **{identified_component}**",
            "audio":None
        })

        # Search Mouser products
        products = search_mouser(identified_component)
        if products:
            st.session_state.history.append({"user":None,"tutor":products,"audio":None})
        else:
            st.session_state.history.append({"user":None,"tutor":"⚠️ No matching parts found on Mouser.","audio":None})

    except Exception as e:
        st.error(f"Image recognition error: {e}")

# -------------------- Text Chat --------------------
user_input = st.text_input("💡 Type your project idea or question:")

if st.button("Send") and user_input.strip():
    products = search_mouser(user_input)
    mouser_products = products if products else []

    tutor_prompt = f"{tutor_system_prompt}\n\nUser project/question: {user_input}"
    try:
        response = chat.send_message(tutor_prompt, stream=True)
        if isinstance(response, list):
            output_text = "".join([chunk.text for chunk in response])
        else:
            output_text = response.text
    except Exception as e:
        output_text = f"❌ Error: {e}"

    output_text = clean_html(output_text)
    audio_data = text_to_speech(output_text)

    st.session_state.history.append({
        "user": user_input,
        "tutor":{"text":output_text,"products":mouser_products},
        "audio":audio_data
    })

# -------------------- Display Chat --------------------
for chat_pair in st.session_state.history:
    if chat_pair.get("user"):
        st.markdown(f"""
            <div style='text-align:right; margin:10px;'>
                <span class='user-bubble'>{html.escape(str(chat_pair['user']))}</span>
            </div>
        """, unsafe_allow_html=True)

    if chat_pair.get("tutor"):
        tutor_content = chat_pair["tutor"]

        if isinstance(tutor_content, list):
            display_mouser_products(tutor_content)
        elif isinstance(tutor_content, str):
            st.markdown(f"""
                <div style='text-align:left; margin:10px;'>
                    <span class='tutor-bubble'>{html.escape(tutor_content)}</span>
                </div>
            """, unsafe_allow_html=True)
        elif isinstance(tutor_content, dict):
            st.markdown(f"""
                <div style='text-align:left; margin:10px;'>
                    <span class='tutor-bubble'>{html.escape(tutor_content.get('text', ''))}</span>
                </div>
            """, unsafe_allow_html=True)
            if tutor_content.get("products"):
                display_mouser_products(tutor_content["products"])

    if chat_pair.get("audio"):
        st.audio(chat_pair["audio"], format="audio/mp3")
