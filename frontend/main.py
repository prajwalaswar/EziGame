import streamlit as st

st.set_page_config(page_title="Medical Voice Assistant", layout="centered")

st.markdown("""
    <style>
        .main-title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: 800;
            margin-top: 2rem;
            margin-bottom: 1.5rem;
            background: linear-gradient(90deg, #00e5ff, #7c4dff, #00e676);
            background-size: 200% auto;
            color: transparent;
            -webkit-background-clip: text;
            background-clip: text;
            animation: gradient 5s linear infinite;
        }
        @keyframes gradient {
            0% { background-position: 0% center; }
            100% { background-position: 200% center; }
        }
        .menu-btn {
            width: 100%;
            padding: 1.2rem;
            font-size: 1.2rem;
            font-weight: 700;
            border-radius: 30px;
            border: none;
            margin-bottom: 1.5rem;
            background: linear-gradient(90deg, #00e676 0%, #00e5ff 100%);
            color: #18122B;
            box-shadow: 0 0 12px #00e67699, 0 0 6px #00e5ff55;
            transition: all 0.2s;
        }
        .menu-btn:hover {
            transform: scale(1.03);
            filter: brightness(1.08);
            box-shadow: 0 8px 24px #7c4dff66, 0 2px 8px #00e5ff66;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🩺 Medical Voice Assistant</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#b0bec5; font-size:1.1rem;">Choose a service below</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("🎙️ Voice-to-Text Analysis", key="voice2text", help="Transcribe and analyze medical conversations", use_container_width=True):
        st.switch_page("pages/streamlit_app.py")
with col2:
    if st.button("🔊 Pure Voice Recording", key="purevoice", help="Record and download audio only", use_container_width=True):
        st.switch_page("pages/pure_voice_recorder.py")
