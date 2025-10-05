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
client = None
if elevenlabs_key:
    client = ElevenLabs(api_key=elevenlabs_key)

def text_to_speech(text, voice="Rachel"):
    # If ElevenLabs client wasn't initialized (no API key), skip TTS
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

# 🌸 Aesthetic Soothing CSS Theme 🌸
st.markdown("""
    <style>
        /* Background Gradient */
        body {
            background: linear-gradient(135deg, #dfe9f3 0%, #ffffff 100%);
            color: #1b1b1b;
            font-family: 'Poppins', sans-serif;
        }

        /* Main Title */
        h1 {
            text-align: center;
            background: linear-gradient(90deg, #78ffd6, #a8edea);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5em;
            margin-bottom: 20px;
        }

        /* Chat Bubbles */
        .user-bubble {
            background: linear-gradient(135deg, #a1c4fd, #c2e9fb);
            color: #1b1b1b;
            padding: 12px 16px;
            border-radius: 18px;
            display: inline-block;
            margin: 8px 0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }

        .tutor-bubble {
            background: linear-gradient(135deg, #fbc2eb, #a6c1ee);
            color: #1b1b1b;
            padding: 12px 16px;
            border-radius: 18px;
            display: inline-block;
            margin: 8px 0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }

        /* Input box */
        input[type="text"] {
            border-radius: 10px !important;
            border: 1px solid #ccc !important;
            background-color: #f9fbfd !important;
            color: #333 !important;
        }

        /* Buttons */
        div.stButton > button {
            background: linear-gradient(135deg, #89f7fe, #66a6ff);
            color: black;
            font-weight: 600;
            border: none;
            border-radius: 10px;
            padding: 0.6em 1.2em;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }

        div.stButton > button:hover {
            background: linear-gradient(135deg, #66a6ff, #89f7fe);
            transform: scale(1.02);
        }

        /* Uploaded image display */
        .uploadedImage {
            border-radius: 12px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }

    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>✨ Electronics & Robotics Chatbot ✨</h1>", unsafe_allow_html=True)

# -------------------- Configure Gemini --------------------
load_dotenv()
# Read GEMINI API key from environment (.env or system env)
gemini_key = "AIzaSyBd09L0gVBmuaTiJ-S3o5jZiuE4zd5892k"

if not gemini_key:
    st.error("❌ GEMINI_API_KEY not found. Please add it to .env file or set the GEMINI_API_KEY environment variable.")
else:
    genai.configure(api_key=gemini_key)

# -------------------- Gemini model setup --------------------
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat()

tutor_system_prompt = """
You are a concise and friendly computer science tutor.
- Give answers in 3-4 short, clear sentences.
- Do NOT include code unless the user explicitly says 'show code' or 'example code'.
- Give one link of site with codes related to the product. 
- If user asks for an electronics part (keywords like 'Arduino', 'ESP32', 'resistor'), 
  respond with a short description and display product image, price, and link (simulate Mouser API).
- End each response with a thank you note.
"""

# -------------------- Mouser API Simulation --------------------
def search_mouser_parts(query):
    url = "https://api.mouser.com/api/v1/search/keyword"
    mouser_api_key = "a165ac49-3ade-43bd-aa1b-885cecae1f48"
    payload = {"SearchByKeywordRequest": {"keyword": query, "records": 5}}
    try:
        response = requests.post(f"{url}?apiKey={mouser_api_key}", json=payload)
        data = response.json()
        products = []
        for item in data.get("SearchResults", {}).get("Parts", []):
            products.append({
                "name": item.get("ManufacturerPartNumber", "Unknown"),
                "link": item.get("ProductDetailUrl", "#")
            })
        return products
    except Exception:
        return []

# -------------------- Chat History --------------------
if "history" not in st.session_state:
    st.session_state.history = []

# -------------------- Image Upload --------------------
uploaded_file = st.file_uploader("📷 Upload an electronic component image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    try:
        image = Image.open(uploaded_file)
        vision_prompt = "Identify the electronic component in this image. Respond only with the component name."
        response = model.generate_content([vision_prompt, image], stream=False)
        identified_component = clean_html(response.text.strip())

        st.image(image, caption="Uploaded Image", use_container_width=True, output_format="PNG")

        st.session_state.history.append({
            "user": "📷 Uploaded an image",
            "tutor": f"🔍 Gemini identified: **{identified_component}**",
            "audio": None
        })

        # Search Mouser
        products = search_mouser_parts(identified_component)
        if products:
            links = "\n".join([f"- [{p['name']}]({p['link']})" for p in products])
            st.session_state.history.append({"user": None, "tutor": f"**🔌 Suggested Mouser Links:**\n{links}", "audio": None})
        else:
            st.session_state.history.append({"user": None, "tutor": "⚠️ No matching parts found on Mouser.", "audio": None})

    except Exception as e:
        st.error(f"Image recognition error: {e}")

# -------------------- Text Chat --------------------
user_input = st.text_input("💡 Type your project idea or question:")

if st.button("Send") and user_input.strip():
    products = search_mouser_parts(user_input)
    mouser_text = "**🔌 Suggested Parts (Buy on Mouser):**\n\n"
    mouser_text += "\n".join([f"- [{p['name']}]({p['link']})" for p in products]) if products else "_No relevant parts found._"

    tutor_prompt = f"{tutor_system_prompt}\n\nUser project/question: {user_input}"
    try:
        response = model.start_chat().send_message(tutor_prompt, stream=True)
        output_text = "".join([chunk.text for chunk in response])
    except Exception as e:
        output_text = f"❌ Error: {e}"

    # Clean and sanitize output
    output_text = clean_html(output_text)
    audio_data = text_to_speech(output_text)

    st.session_state.history.append({
        "user": user_input,
        "tutor": mouser_text + "\n\n" + output_text,
        "audio": audio_data
    })

# -------------------- Display Chat --------------------
for chat_pair in st.session_state.history:
    if chat_pair.get("user"):
        st.markdown(f"""
            <div style='text-align:right; margin:10px;'>
                <span class='user-bubble'>{html.escape(chat_pair['user'])}</span>
            </div>
        """, unsafe_allow_html=True)

    if chat_pair.get("tutor"):
        st.markdown(f"""
            <div style='text-align:left; margin:10px;'>
                <span class='tutor-bubble'>{html.escape(chat_pair['tutor'])}</span>
            </div>
        """, unsafe_allow_html=True)

    if chat_pair.get("audio"):
        st.audio(chat_pair["audio"], format="audio/mp3")