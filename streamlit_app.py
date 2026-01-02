"""Streamlit frontend for Vietnamese Translation API."""

import streamlit as st
import requests
import json
from datetime import datetime
import os
import io
import numpy as np

from scipy.io import wavfile

# Page configuration
st.set_page_config(
    page_title="Vietnamese Translation",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 18px;
        padding: 10px 20px;
    }
    .result-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        margin-top: 20px;
    }
    .confidence-badge {
        background-color: #e3f2fd;
        padding: 10px 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# API Configuration
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")

def make_api_call(endpoint: str, method: str = "GET", data=None, files=None):
    """Make API calls to the backend."""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files)
            elif data:
                response = requests.post(url, json=data)
            else:
                response = requests.post(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}


# Header
st.title("🌐 Vietnamese Translation Service")
st.markdown("Real-time Vietnamese ↔ English translation powered by Whisper & GPT-4o Mini")

# Sidebar
with st.sidebar:
    st.header("Settings")
    api_url = st.text_input("API URL", value=API_BASE_URL, help="Backend API endpoint")
    if api_url != API_BASE_URL:
        os.environ["API_URL"] = api_url
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    - **Audio Processing**: OpenAI Whisper
    - **Translation**: GPT-4o Mini
    - **Backend**: FastAPI
    - **Frontend**: Streamlit
    """)

# Main tabs
tab1, tab2, tab3 = st.tabs(["📝 Text Translation", "🎤 Audio Translation", "📚 History"])

# ==================== TAB 1: TEXT TRANSLATION ====================
with tab1:
    st.header("Text Translation")
    st.markdown("Translate Vietnamese text to English")
    
    # Text input
    col1, col2 = st.columns([3, 1])
    with col1:
        text_input = st.text_area(
            "Enter Vietnamese text:",
            placeholder="Type or paste Vietnamese text here...",
            height=150,
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("")
        translate_btn = st.button("🚀 Translate", key="text_translate", use_container_width=True)
    
    # Process text translation
    if translate_btn:
        if not text_input.strip():
            st.error("❌ Please enter text to translate")
        else:
            with st.spinner("🔄 Translating..."):
                result = make_api_call(
                    "/api/translate/text",
                    method="POST",
                    data={
                        "text": text_input,
                        "source_language": "vi",
                        "target_language": "en"
                    }
                )
            
            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.success("✅ Translation Complete!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### Vietnamese (Source)")
                    st.write(result.get("source_text", ""))
                
                with col2:
                    st.markdown("### English (Target)")
                    st.write(result.get("translated_text", ""))
                
                st.markdown("---")
                st.caption(f"Translation ID: {result.get('translation_id')} | {result.get('timestamp')}")

# ==================== TAB 2: AUDIO TRANSLATION ====================
with tab2:
    st.header("Audio File Translation")
    st.markdown("Upload an audio file to transcribe and translate")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Select an audio file (WAV, MP3, OGG, FLAC)",
            type=["wav", "mp3", "ogg", "flac"],
            label_visibility="collapsed"
        )
    
    # Show file size warning if needed
    if uploaded_file:
        file_size_mb = len(uploaded_file.getbuffer()) / (1024 * 1024)
        size_color = "🟡" if file_size_mb > 20 else "🟢"
        st.info(f"{size_color} File size: {file_size_mb:.1f} MB")
        
        if file_size_mb > 25:
            st.warning("⚠️ Large file detected! Will be processed in chunks. This may take longer.")
        elif file_size_mb > 20:
            st.info("ℹ️ File is close to the 25 MB limit. Processing may take longer.")
    
    with col2:
        st.markdown("")
        process_btn = st.button("🔄 Process Audio", key="audio_translate", use_container_width=True)
    
    # Process audio
    if process_btn:
        if not uploaded_file:
            st.error("❌ Please upload an audio file")
        else:
            try:
                with st.spinner("🎵 Processing audio..."):
                    # Copy file data to BytesIO to avoid buffer conflicts
                    import io
                    file_bytes = io.BytesIO(uploaded_file.read())
                    
                    files = {"file": (uploaded_file.name, file_bytes, uploaded_file.type)}
                    result = make_api_call(
                        "/api/translate/audio",
                        method="POST",
                        files=files
                    )
                
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success("✅ Audio Processing Complete!")
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Vietnamese Transcription")
                        st.write(result.get("source_text", ""))
                    
                    with col2:
                        st.markdown("### English Translation")
                        st.write(result.get("translated_text", ""))
                    
                    # Metadata
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        duration = result.get("duration_seconds", 0)
                        st.metric("Duration", f"{duration:.2f}s")
                    
                    with col2:
                        confidence = result.get("confidence", 0)
                        confidence_pct = confidence * 100
                        st.metric("Confidence", f"{confidence_pct:.1f}%")
                    
                    with col3:
                        st.metric("Translation ID", result.get("translation_id", "N/A"))
            except Exception as e:
                st.error(f"❌ Processing failed: {str(e)}")

# ==================== TAB 3: HISTORY ====================
with tab3:
    st.header("Translation History")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        limit = st.number_input("Show last", min_value=5, max_value=100, value=20, step=5)
    
    with col2:
        if st.button("🔄 Refresh History", use_container_width=True):
            st.rerun()
    
    # Fetch history
    with st.spinner("📚 Loading translation history..."):
        history = make_api_call(f"/api/history?limit={limit}")
    
    if "error" in history:
        st.error(f"Error loading history: {history['error']}")
    elif not history.get("translations"):
        st.info("📭 No translations yet. Start by translating some text or audio!")
    else:
        # Display stats
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Translations", history.get("total_translations", 0))
        
        with col2:
            st.metric("Showing", history.get("returned", 0))
        
        with col3:
            if history.get("translations"):
                avg_confidence = sum(t.get("confidence", 0) for t in history["translations"]) / len(history["translations"])
                st.metric("Avg Confidence", f"{avg_confidence*100:.1f}%")
        
        st.markdown("---")
        
        # Display translations
        for i, translation in enumerate(reversed(history.get("translations", [])), 1):
            with st.expander(
                f"**{i}. {translation.get('source_text', '')[:50]}...** | {translation.get('timestamp', '').split('T')[0]}"
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Vietnamese (Source)**")
                    st.write(translation.get("source_text", ""))
                
                with col2:
                    st.markdown("**English (Target)**")
                    st.write(translation.get("translated_text", ""))
                
                # Metadata
                st.markdown("---")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.caption(f"📅 **Date**: {translation.get('timestamp', '').split('T')[0]}")
                
                with col2:
                    st.caption(f"⏱️ **Time**: {translation.get('timestamp', '').split('T')[1][:5]}")
                
                with col3:
                    duration = translation.get("duration_seconds", 0)
                    if duration:
                        st.caption(f"⏳ **Duration**: {duration:.2f}s")
                
                with col4:
                    confidence = translation.get("confidence", 0)
                    if confidence:
                        st.caption(f"🎯 **Confidence**: {confidence*100:.1f}%")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
    <small>Vietnamese Translation Service | Powered by OpenAI Whisper & GPT-4o Mini</small>
    </div>
    """,
    unsafe_allow_html=True
)
