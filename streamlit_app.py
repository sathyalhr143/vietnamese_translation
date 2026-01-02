"""Streamlit frontend for Vietnamese Translation - Direct Execution Mode."""

import streamlit as st
import os
import io
from datetime import datetime
import tempfile
import sys

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Check if OPENAI_API_KEY is set
if not os.getenv('OPENAI_API_KEY'):
    st.error("""
    ⚠️ **Missing OPENAI_API_KEY Configuration**
    
    This app requires an OpenAI API key to function. Please set it up:
    
    **Option 1: Environment Variable**
    ```bash
    export OPENAI_API_KEY='your-api-key-here'
    streamlit run streamlit_app.py
    ```
    
    **Option 2: .env File**
    Create a `.env` file in the project root:
    ```
    OPENAI_API_KEY=your-api-key-here
    ```
    
    **Option 3: Streamlit Cloud Secrets**
    Go to your app settings → Secrets → Add `OPENAI_API_KEY`
    
    Get your API key from: https://platform.openai.com/api-keys
    """)
    st.stop()

# Lazy import - delay until after API key check
# This prevents import errors on Streamlit Cloud where packages might not be installed yet

# Page configuration
st.set_page_config(
    page_title="Vietnamese Translation",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling - Dark VS Code Theme
st.markdown("""
    <style>
    :root {
        --primary-bg: #1e1e1e;
        --secondary-bg: #252526;
        --tertiary-bg: #2d2d30;
        --text-primary: #e0e0e0;
        --text-secondary: #a0a0a0;
        --accent-blue: #007acc;
        --accent-cyan: #4ec9b0;
        --accent-yellow: #dcdcaa;
    }
    
    body, .main, .stApp {
        background-color: var(--primary-bg) !important;
        color: var(--text-primary) !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #1e1e1e 0%, #252526 100%);
    }
    
    .main {
        padding-top: 2rem;
        background-color: var(--primary-bg);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: var(--secondary-bg) !important;
        border-right: 1px solid var(--tertiary-bg);
    }
    
    section[data-testid="stSidebar"] > div {
        background-color: var(--secondary-bg) !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--secondary-bg);
        border-bottom: 1px solid var(--tertiary-bg);
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
        padding: 12px 20px;
        color: var(--text-secondary);
        background-color: transparent;
        border: none;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: var(--accent-blue);
        border-bottom: 2px solid var(--accent-blue);
        background-color: rgba(0, 122, 204, 0.1);
    }
    
    .stTabs [data-baseweb="tab-list"] button:hover {
        color: var(--accent-cyan);
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: var(--accent-cyan) !important;
    }
    
    h1 {
        border-bottom: 1px solid var(--tertiary-bg);
        padding-bottom: 1rem;
    }
    
    /* Text areas and inputs */
    .stTextArea > div > div > textarea {
        background-color: var(--secondary-bg) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--tertiary-bg) !important;
        border-radius: 6px;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 8px rgba(0, 122, 204, 0.3) !important;
    }
    
    input[type="text"], input[type="number"] {
        background-color: var(--secondary-bg) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--tertiary-bg) !important;
        border-radius: 4px;
    }
    
    input[type="text"]:focus, input[type="number"]:focus {
        border-color: var(--accent-blue) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: var(--accent-blue) !important;
        color: white !important;
        border: none !important;
        border-radius: 4px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #0098ff !important;
        box-shadow: 0 0 12px rgba(0, 122, 204, 0.4) !important;
    }
    
    .stButton > button:active {
        background-color: #0066cc !important;
    }
    
    /* Result boxes */
    .result-box {
        background-color: var(--tertiary-bg);
        border-left: 3px solid var(--accent-blue);
        padding: 20px;
        border-radius: 8px;
        margin-top: 20px;
        color: var(--text-primary);
    }
    
    /* Confidence badge */
    .confidence-badge {
        background-color: rgba(0, 122, 204, 0.15);
        border: 1px solid var(--accent-blue);
        padding: 10px 15px;
        border-radius: 6px;
        margin: 10px 0;
        color: var(--accent-cyan);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: var(--secondary-bg) !important;
        color: var(--text-primary) !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: var(--tertiary-bg) !important;
    }
    
    /* Metrics */
    .stMetric {
        background-color: var(--secondary-bg);
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid var(--tertiary-bg);
    }
    
    .stMetric > div > div > div > h3 {
        color: var(--text-secondary) !important;
        font-size: 0.8rem;
    }
    
    .stMetric > div > div > div > div {
        color: var(--accent-cyan) !important;
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    /* Info, Success, Warning, Error messages */
    .stAlert {
        border-radius: 6px;
        border: 1px solid;
    }
    
    [data-testid="stAlert"] {
        border-radius: 6px;
    }
    
    /* Toolbar and header area */
    [data-testid="stToolbar"] {
        background-color: var(--secondary-bg) !important;
        border-bottom: 1px solid var(--tertiary-bg) !important;
    }
    
    [data-testid="stDecoration"] {
        background-color: var(--primary-bg) !important;
    }
    
    /* Top right buttons (rerun, settings, etc) */
    button[kind="secondary"] {
        background-color: var(--secondary-bg) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--tertiary-bg) !important;
    }
    
    button[kind="secondary"]:hover {
        background-color: var(--tertiary-bg) !important;
        border-color: var(--accent-blue) !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: var(--secondary-bg);
        border: 2px dashed var(--accent-blue);
        border-radius: 8px;
        padding: 20px;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--secondary-bg);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--tertiary-bg);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-blue);
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize services once per session
@st.cache_resource
def initialize_services():
    """Initialize translator, audio processor, and database."""
    try:
        # Import here to delay until after API key check
        from src.translator import Translator
        from src.audio import AudioProcessor
        from src.database import TranslationDatabase
        
        translator = Translator()
        audio_processor = AudioProcessor()
        database = TranslationDatabase()
        return translator, audio_processor, database
    except ImportError as e:
        st.error(f"""
        ❌ **Import Error**: {str(e)}
        
        Missing dependency. This usually means a package didn't install properly on Streamlit Cloud.
        Try redeploying the app or check the logs for more details.
        """)
        st.stop()
    except ValueError as e:
        if "OPENAI_API_KEY" in str(e):
            st.error("""
            ⚠️ **API Key Error**
            
            The OPENAI_API_KEY is not set. Please configure it:
            - Set environment variable: `export OPENAI_API_KEY='your-key'`
            - Or add to .env file: `OPENAI_API_KEY=your-key`
            - Or add to Streamlit Cloud secrets
            """)
        else:
            st.error(f"Error initializing services: {str(e)}")
        st.stop()

try:
    translator, audio_processor, database = initialize_services()
except Exception as e:
    st.error(f"Failed to initialize services: {str(e)}")
    st.stop()

# Header
st.title("🌐 Vietnamese Translation Service")
st.markdown("Real-time Vietnamese ↔ English translation powered by Whisper & GPT-4o Mini")

# Sidebar
with st.sidebar:
    st.header("Settings")
    st.markdown("### About")
    st.markdown("""
    - **Audio Processing**: OpenAI Whisper
    - **Translation**: GPT-4o Mini
    - **Database**: SQLite (Local)
    - **Frontend**: Streamlit
    
    **Running in Direct Execution Mode** - All processing happens locally without a separate backend server.
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
                try:
                    from src.models import TranslationRecord
                    
                    # Call translator directly
                    translated_text = translator.translate_text(text_input)
                    
                    # Store in database
                    record = TranslationRecord(
                        source_language="vi",
                        target_language="en",
                        source_text=text_input,
                        translated_text=translated_text,
                        confidence=1.0,  # Text translation has high confidence
                        duration_seconds=0
                    )
                    translation_id = database.insert_translation(record)
                    
                    # Display results
                    st.success("✅ Translation Complete!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### Vietnamese (Source)")
                        st.write(text_input)
                    
                    with col2:
                        st.markdown("### English (Target)")
                        st.write(translated_text)
                    
                    st.markdown("---")
                    st.caption(f"Translation ID: {translation_id} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                except Exception as e:
                    st.error(f"❌ Translation failed: {str(e)}")

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
                    # Save uploaded file to temporary location
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        tmp_path = tmp_file.name
                    
                    try:
                        # Transcribe audio directly
                        transcription_result = audio_processor.transcribe_audio_from_file_chunked(tmp_path)
                        vietnamese_text = transcription_result.text
                        confidence = transcription_result.confidence
                        duration = transcription_result.duration
                        
                        # Translate transcribed text
                        english_text = translator.translate_text(vietnamese_text)
                        
                        # Store in database
                        from src.models import TranslationRecord
                        record = TranslationRecord(
                            source_language="vi",
                            target_language="en",
                            source_text=vietnamese_text,
                            translated_text=english_text,
                            confidence=confidence,
                            duration_seconds=duration
                        )
                        translation_id = database.insert_translation(record)
                        
                        # Display results
                        st.success("✅ Audio Processing Complete!")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### Vietnamese Transcription")
                            st.write(vietnamese_text)
                        
                        with col2:
                            st.markdown("### English Translation")
                            st.write(english_text)
                        
                        # Metadata
                        st.markdown("---")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Duration", f"{duration:.2f}s")
                        
                        with col2:
                            confidence_pct = confidence * 100
                            st.metric("Confidence", f"{confidence_pct:.1f}%")
                        
                        with col3:
                            st.metric("Translation ID", translation_id)
                    
                    finally:
                        # Clean up temporary file
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)
                
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
    
    with col3:
        if st.button("🗑️ Clear All History", use_container_width=True):
            try:
                # Clear all translations from database
                conn = __import__('sqlite3').connect(database.db_path)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM translations')
                cursor.execute('DELETE FROM audio_metadata')
                conn.commit()
                conn.close()
                st.success("✅ History cleared!")
                st.rerun()
            except Exception as e:
                st.error(f"Error clearing history: {str(e)}")
    
    # Fetch history
    with st.spinner("📚 Loading translation history..."):
        try:
            history_records = database.get_all_translations()
            total_count = len(history_records)
            
            # Apply limit to display
            limit = int(limit)
            displayed_records = history_records[:limit]
            
            if not history_records:
                st.info("📭 No translations yet. Start by translating some text or audio!")
            else:
                # Display stats
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Translations", total_count)
                
                with col2:
                    st.metric("Showing", len(displayed_records))
                
                with col3:
                    if displayed_records:
                        avg_confidence = sum(r.confidence or 0 for r in displayed_records) / len(displayed_records)
                        st.metric("Avg Confidence", f"{avg_confidence*100:.1f}%")
                
                st.markdown("---")
                
                # Display translations
                for i, translation in enumerate(displayed_records, 1):
                    timestamp = translation.timestamp or "Unknown"
                    date_part = timestamp.split()[0] if timestamp else "Unknown"
                    source_preview = translation.source_text[:50]
                    
                    with st.expander(
                        f"**{i}. {source_preview}...** | {date_part}"
                    ):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Vietnamese (Source)**")
                            st.write(translation.source_text)
                        
                        with col2:
                            st.markdown("**English (Target)**")
                            st.write(translation.translated_text)
                        
                        # Metadata
                        st.markdown("---")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.caption(f"📅 **Date**: {date_part}")
                        
                        with col2:
                            time_part = timestamp.split()[1][:5] if len(timestamp.split()) > 1 else "N/A"
                            st.caption(f"⏱️ **Time**: {time_part}")
                        
                        with col3:
                            if translation.duration_seconds:
                                st.caption(f"⏳ **Duration**: {translation.duration_seconds:.2f}s")
                        
                        with col4:
                            if translation.confidence:
                                st.caption(f"🎯 **Confidence**: {translation.confidence*100:.1f}%")
        
        except Exception as e:
            st.error(f"Error loading history: {str(e)}")

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
