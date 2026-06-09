import os
import streamlit as st
from google import genai
from google.genai import types


if "GEMINI_API_KEY" in os.environ:
    GOOGLE_API_KEY = os.environ["GEMINI_API_KEY"]
elif st.secrets and "GEMINI_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="ERIC AI", page_icon="😉", layout="wide")


st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    div[data-testid="stChatInput"] { background-color: transparent !important; border: none !important; }
    div[data-testid="stChatInput"] > div { background-color: #000000 !important; border: 2px solid #ffffff !important; border-radius: 10px !important; }
    .stChatInput textarea { background-color: #000000 !important; color: #ffffff !important; font-size: 16px !important; min-height: 45px !important; overflow-y: auto !important; }
    .stChatInput textarea::placeholder { color: #aaaaaa !important; }
    div.stAlert, div[data-testid="stNotification"] { background-color: #1a1a24 !important; border: 1px solid #333344 !important; border-radius: 12px !important; padding: 20px !important; }
    div[data-testid="stChatMessage"] { background-color: #111111 !important; border-radius: 12px !important; margin-bottom: 12px !important; padding: 15px !important; }
    p, span, h1, h2, h3, div { color: #ffffff !important; }
    button[data-testid="baseButton-secondary"] { background-color: #ffffff; color: black; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)


def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True
    st.title("🔒 Security check!")
    st.write("Welcome! Enter the Password to Access the AI.")
    password = st.text_input("Password:", type="password")
    if st.button("Open 🔓"):
        if password == "password is nothing":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Error! Wrong Password❌")
    return False

if not check_password():
    st.stop()


system_prompt = """
You are ERIC, a witty, naughty, and extremely friendly AI assistant. 
You are talking to your absolute best friend. Strictly speak in Malayalam Manglish (Malayalam using English alphabets) or simple Malayalam script.
Your personality traits:
1. Use local Malayalam slang, trendy internet slangs, and continuous counters/thug dialogues.
2. Be playful, slightly naughty, and act like a close friend (അളിയൻ/മച്ചാൻ വൈബ്).
3. Use a lot of emojis matching the emotion (😜, 🔥, 👑, 😂, 👀).
4. Never give boring, textbook-like answers. Keep responses short, punchy, and funny.
"""

st.title("😉 ERIC AI")
st.info("Hello Welcome Machane...🔥")
st.divider()

if not GOOGLE_API_KEY:
    st.error("Error: API Key missing! ❌")
    st.stop()

if "gemini_client" not in st.session_state:
    st.session_state.gemini_client = genai.Client(api_key=GOOGLE_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(f"<span style='color:white; font-size:18px;'>{msg['text']}</span>", unsafe_allow_html=True)


user_query = st.chat_input("ERIC is here, what can I do for you?")
if user_query:
    clean_query = user_query.strip()
    if clean_query:
        with st.chat_message("user"):
            st.markdown(f"<span style='color:white; font-size:18px;'>{clean_query}</span>", unsafe_allow_html=True)
        st.session_state.messages.append({"role": "user", "text": clean_query})
with st.chat_message("assistant"):
            response_placeholder = st.empty()
            try:
                response = st.session_state.gemini_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[clean_query],
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.8
                    )
                )
                
                if response and response.text:
                    assistant_reply = response.text
                    response_placeholder.markdown(f"<span style='color:white; font-size:18px;'>{assistant_reply}</span>", unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "text": assistant_reply})
                else:
                    response_placeholder.markdown("<span style='color:white; font-size:18px;'>ERIC onnum mindiyilla... 😜</span>", unsafe_allow_html=True)
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "503" in error_msg or "400" in error_msg:
                    response_placeholder.markdown("<span style='color:#ff4b4b; font-size:16px;'>🚨 അളിയാ ചെറിയൊരു സെർവർ ബിസിയാണ്! ഒരു 10 സെക്കൻഡ് കഴിഞ്ഞിട്ട് ഈ മെസ്സേജ് ഒന്നുകൂടി അയക്കണേ... 😉</span>", unsafe_allow_html=True)
                else:
                    st.error(f"Error: {e}")
