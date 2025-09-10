import streamlit as st
import os
import sqlite3
import google.generativeai as genai
import speech_recognition as sr
import tempfile
import pandas as pd
import numpy as np
import io
import wave
import datetime
import time
from dotenv import load_dotenv

# Import our project-specific modules
from document_processor import process_documents
from query_handler import process_query
from sql_fin_exp import InsuranceClaimsDatabase  # Import the new database class

# Try to import psutil for process detection, fallback if not available
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# --- Initial Setup ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
st.set_page_config(page_title="Document Processing & Chat", layout="wide")


# ############################################################################
# START OF PROVIDED CHATBOT CODE (INTEGRATED AND MODIFIED)
# ############################################################################

# Language translations for the entire interface
def get_interface_translations():
    """Get all interface text translations"""
    return {
        "English": {
            "main_title": "🎓 Insurance Claims Assistant",
            "subtitle": "Ask questions about insurance data using your voice or text",
            "chat_with_us": "💬 Chat with Us",
            "settings": "⚙️ Settings",
            "voice_settings": "🎤 Voice Settings",
            "listen_duration": "How long should I listen? (seconds)",
            "voice_auto_submit_info": "💡 **Voice Auto-Submit:** Speak for more than 5 seconds and your question will be submitted automatically!",
            "need_help": "❓ Need Help?",
            "show_help_guide": "📚 Show Help Guide",
            "recent_searches": "🕐 Recent Searches",
            "ask_question": "💬 Ask Your Question",
            "question_placeholder": "Type your question here and press Enter... (e.g., 'How many active policies are there?')",
            "submit": "Submit",
            "press_enter_hint": "💡 **Press Enter** to submit your question",
            "auto_submit_voice": "🚀 Auto-submitting your voice question...",
            "processing_selected": "🚀 Processing your selected question...",
            "processing_question": "⌨️ Processing your question...",
            "finding_answer": "🔄 Finding your answer...",
            "results_found": "📊 Here's what I found:",
            "found_results": "✅ Found {count} result(s)",
            "no_results": "🤔 I couldn't find any results for your question.",
            "try_different": "💡 Try asking in a different way or use one of the popular questions below.",
            "something_wrong": "😕 Something went wrong. Please try asking your question in a different way.",
            "try_these": "💡 **Try these instead:**",
            "ask_question_first": "⚠️ Please ask a question first!",
            "use_voice": "### 🎤 Or Use Your Voice",
            "voice_auto_hint": "💡 Speak for more than 5 seconds for automatic submission!",
            "voice_disabled": "🚫 **Voice input disabled due to microphone conflict**",
            "check_microphone": "🔄 Check Microphone Again",
            "start_speaking": "🎤 Start Speaking",
            "upload_audio": "📁 Or Upload Audio File",
            "upload_hint": "💡 Supported formats: WAV (recommended), MP3, MP4, M4A • Max size: 25MB",
            "choose_audio": "Choose an audio file",
            "upload_help": "Upload a clear audio recording with your question. WAV format works best.",
            "file_too_large": "❌ File too large! Please upload a file smaller than 25MB.",
            "process_audio": "🔄 Process Audio File",
            "processing_audio": "Processing your audio file...",
            "audio_success": "✅ I heard: {text}",
            "audio_failed": "❌ Could not process your audio file.",
            "audio_solutions": "💡 **Try these solutions:**",
            "popular_questions": "🔥 Popular Questions",
            "click_instant": "Click any question below for instant results!",
            "back_to_main": "← Back to Main",
            "footer_text": "🎓 **Insurance Claims Assistant** | Ask questions naturally with voice or text",
            "footer_help": "💡 Need help? Click \"Chat with Us\" for instant support!",
            "quick_keywords": [
                "Voice Input Issues", "Database Questions", "How to Use",
                "Technical Problems", "Audio Upload", "Results Not Showing",
                "Getting Started", "Account Issues", "Performance Issues"
            ],
            "quick_queries": [
                "How many policies are active?",
                "Show all claims from Mumbai",
                "List insured persons with 'Diabetes' as a pre-existing condition",
                "What is the total approved amount for all claims?",
                "Show all rejected claims",
                "What are the details for claim CLM_001?"
            ]
        },
        "Hindi": {
            "main_title": "🎓 बीमा दावा सहायक",
            "subtitle": "अपनी आवाज़ या टेक्स्ट का उपयोग करके बीमा डेटा के बारे में प्रश्न पूछें",
            "chat_with_us": "💬 हमसे चैट करें",
            "settings": "⚙️ सेटिंग्स",
            "voice_settings": "🎤 आवाज़ सेटिंग्स",
            "listen_duration": "मुझे कितनी देर सुनना चाहिए? (सेकंड)",
            "voice_auto_submit_info": "💡 **आवाज़ ऑटो-सबमिट:** 5 सेकंड से अधिक बोलें और आपका प्रश्न स्वचालित रूप से जमा हो जाएगा!",
            "need_help": "❓ मदद चाहिए?",
            "show_help_guide": "📚 सहायता गाइड दिखाएं",
            "recent_searches": "🕐 हाल की खोजें",
            "ask_question": "💬 अपना प्रश्न पूछें",
            "question_placeholder": "यहाँ अपना प्रश्न टाइप करें और Enter दबाएं... (जैसे, 'कितनी पॉलिसियां सक्रिय हैं?')",
            "submit": "जमा करें",
            "press_enter_hint": "💡 **Enter दबाएं** अपना प्रश्न जमा करने के लिए",
            "auto_submit_voice": "🚀 आपके आवाज़ के प्रश्न को ऑटो-सबमिट कर रहे हैं...",
            "processing_selected": "🚀 आपके चुने गए प्रश्न को प्रोसेस कर रहे हैं...",
            "processing_question": "⌨️ आपके प्रश्न को प्रोसेस कर रहे हैं...",
            "finding_answer": "🔄 आपका उत्तर खोज रहे हैं...",
            "results_found": "📊 यह मिला:",
            "found_results": "✅ {count} परिणाम मिले",
            "no_results": "🤔 मुझे आपके प्रश्न का कोई परिणाम नहीं मिला।",
            "try_different": "💡 अलग तरीके से पूछने की कोशिश करें या नीचे के लोकप्रिय प्रश्नों का उपयोग करें।",
            "something_wrong": "😕 कुछ गलत हुआ। कृपया अपना प्रश्न अलग तरीके से पूछने की कोशिश करें।",
            "try_these": "💡 **इनको आज़माएं:**",
            "ask_question_first": "⚠️ कृपया पहले एक प्रश्न पूछें!",
            "use_voice": "### 🎤 या अपनी आवाज़ का उपयोग करें",
            "voice_auto_hint": "💡 स्वचालित सबमिशन के लिए 5 सेकंड से अधिक बोलें!",
            "voice_disabled": "🚫 **माइक्रोफ़ोन संघर्ष के कारण आवाज़ इनपुट अक्षम**",
            "check_microphone": "🔄 माइक्रोफ़ोन फिर से जांचें",
            "start_speaking": "🎤 बोलना शुरू करें",
            "upload_audio": "📁 या ऑडियो फ़ाइल अपलोड करें",
            "upload_hint": "💡 समर्थित प्रारूप: WAV (अनुशंसित), MP3, MP4, M4A • अधिकतम आकार: 25MB",
            "choose_audio": "एक ऑडियो फ़ाइल चुनें",
            "upload_help": "अपने प्रश्न के साथ एक स्पष्ट ऑडियो रिकॉर्डिंग अपलोड करें। WAV प्रारूप सबसे अच्छा काम करता है।",
            "file_too_large": "❌ फ़ाइल बहुत बड़ी! कृपया 25MB से छोटी फ़ाइल अपलोड करें।",
            "process_audio": "🔄 ऑडियो फ़ाइल प्रोसेस करें",
            "processing_audio": "आपकी ऑडियो फ़ाइल प्रोसेस कर रहे हैं...",
            "audio_success": "✅ मैंने सुना: {text}",
            "audio_failed": "❌ आपकी ऑडियो फ़ाइल प्रोसेस नहीं कर सका।",
            "audio_solutions": "💡 **इन समाधानों को आज़माएं:**",
            "popular_questions": "🔥 लोकप्रिय प्रश्न",
            "click_instant": "तुरंत परिणाम के लिए नीचे किसी भी प्रश्न पर क्लिक करें!",
            "back_to_main": "← मुख्य पर वापस",
            "footer_text": "🎓 **बीमा दावा सहायक** | आवाज़ या टेक्स्ट के साथ प्राकृतिक रूप से प्रश्न पूछें",
            "footer_help": "💡 मदद चाहिए? तुरंत सहायता के लिए \"हमसे चैट करें\" पर क्लिक करें!",
            "quick_keywords": [
                "आवाज़ इनपुट समस्याएं", "डेटाबेस प्रश्न", "उपयोग कैसे करें",
                "तकनीकी समस्याएं", "ऑडियो अपलोड", "परिणाम नहीं दिख रहे",
                "शुरुआत करना", "खाता समस्याएं", "प्रदर्शन समस्याएं"
            ],
            "quick_queries": [
                "कितनी पॉलिसियां सक्रिय हैं?",
                "मुंबई से सभी दावे दिखाएं",
                "'मधुमेह' के साथ बीमित व्यक्तियों की सूची बनाएं",
                "सभी दावों की कुल स्वीकृत राशि क्या है?",
                "सभी अस्वीकृत दावे दिखाएं",
                "दावा CLM_001 का विवरण क्या है?"
            ]
        },
        # NOTE: For brevity, translations for Telugu, Tamil, and Bengali are omitted here but were included in the original chatbot code.
        # You can add them back in if needed.
    }


# Initialize session state for language preference
if "user_language" not in st.session_state:
    st.session_state.user_language = "English"


def get_text(key):
    """Get translated text based on current language"""
    translations = get_interface_translations()
    return translations[st.session_state.user_language].get(key, translations["English"].get(key, key))


# Chat support related functions
def get_chatbot_response(user_message, language="English"):
    """Get response from chatbot in specified language"""
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')

        chat_prompt = f"""
        You are a helpful and friendly customer support assistant for an Insurance Claims Assistant application.

        Guidelines:
        - Respond in the {language} language.
        - Be helpful, polite, and professional but friendly.
        - Keep responses concise and clear.
        - If the user asks technical questions about the app, provide helpful guidance.
        - If the issue is complex, suggest contacting a customer executive.
        - Use appropriate emojis to make responses friendly.

        User message: {user_message}

        Provide a helpful response:
        """

        response = model.generate_content(chat_prompt)
        return response.text.strip()
    except Exception as e:
        return f"I apologize, but I'm having trouble responding right now. Please try again or contact our customer executive. 😊"


def get_keywords_in_language(language):
    """Get keywords translated for the selected language"""
    translations = get_interface_translations()
    return translations.get(language, translations["English"])["quick_keywords"]


def get_keyword_mapping():
    """Get mapping of translated keywords back to English for processing"""
    return {
        # Hindi mappings
        "आवाज़ इनपुट समस्याएं": "Voice Input Issues",
        "डेटाबेस प्रश्न": "Database Questions",
        "उपयोग कैसे करें": "How to Use",
        "तकनीकी समस्याएं": "Technical Problems",
        "ऑडियो अपलोड": "Audio Upload",
        "परिणाम नहीं दिख रहे": "Results Not Showing",
        "शुरुआत करना": "Getting Started",
        "खाता समस्याएं": "Account Issues",
        "प्रदर्शन समस्याएं": "Performance Issues",
        # Add other language mappings here if needed
    }


def show_chat_page():
    """Render the chat support interface"""
    st.markdown("""
    <style>
        .chat-container {
            max-height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            margin: 20px 0;
        }

        .chat-message {
            margin: 10px 0;
            padding: 12px 16px;
            border-radius: 18px;
            max-width: 80%;
            word-wrap: break-word;
        }

        .user-message {
            background: #ffffff;
            color: #333;
            margin-left: auto;
            margin-right: 0;
            text-align: right;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .bot-message {
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            color: #2c3e50;
            margin-left: 0;
            margin-right: auto;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .keyword-button {
            background: linear-gradient(45deg, #ff6b6b, #ffa500);
            color: white;
            border: none;
            padding: 8px 16px;
            margin: 5px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
        }

        .keyword-button:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        .call-executive-btn {
            background: linear-gradient(45deg, #e74c3c, #c0392b);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        .call-executive-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }

        .language-selector {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 10px;
            margin: 10px 0;
        }

        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Chat header
    st.markdown("""
    <div class="chat-header">
        <h2>💬 Chat with Us! We're Here to Help! 🤗</h2>
        <p>Ask us anything in your preferred language</p>
    </div>
    """, unsafe_allow_html=True)

    # Language selection
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_language = st.selectbox(
            "🌍 Choose your language:",
            ["English", "Hindi", "Telugu", "Tamil", "Marathi", "Bengali", "Gujarati", "Kannada", "Malayalam",
             "Punjabi"],
            key="chat_language"
        )

    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "bot",
                "content": f"Hello! 👋 I'm here to help you with any questions about our Insurance Claims Assistant. How can I assist you today? 😊",
                "timestamp": datetime.datetime.now()
            }
        ]

    # Keywords section (translated)
    st.markdown("### 🔍 Quick Help Keywords")
    st.caption("Click on any keyword for instant help!")

    keywords = get_keywords_in_language(selected_language)

    # Display keywords in grid
    cols = st.columns(3)
    for i, keyword in enumerate(keywords):
        with cols[i % 3]:
            if st.button(f"🔧 {keyword}", key=f"keyword_{i}"):
                # Auto-submit keyword question
                keyword_response = get_keyword_response(keyword, selected_language)
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": keyword,
                    "timestamp": datetime.datetime.now()
                })
                st.session_state.chat_messages.append({
                    "role": "bot",
                    "content": keyword_response,
                    "timestamp": datetime.datetime.now()
                })
                st.rerun()

    # Chat display area
    st.markdown("### 💭 Chat History")

    # Create chat container
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.chat_messages[-10:]:  # Show last 10 messages
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                    <br><small>{message["timestamp"].strftime("%H:%M")}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>Assistant:</strong> {message["content"]}
                    <br><small>{message["timestamp"].strftime("%H:%M")}</small>
                </div>
                """, unsafe_allow_html=True)

    # Chat input
    st.markdown("### ✏️ Type Your Message")

    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "",
            placeholder=f"Type your message in {selected_language}...",
            height=100,
            label_visibility="collapsed"
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            chat_submit = st.form_submit_button("📤 Send Message", use_container_width=True)

    if chat_submit and user_input:
        # Add user message
        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.datetime.now()
        })

        # Get bot response
        with st.spinner("🤔 Thinking..."):
            bot_response = get_chatbot_response(user_input, selected_language)

        # Add bot response
        st.session_state.chat_messages.append({
            "role": "bot",
            "content": bot_response,
            "timestamp": datetime.datetime.now()
        })

        st.rerun()

    # Call executive button
    st.markdown("### 📞 Need More Help?")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📞 Call Customer Executive", key="call_executive"):
            show_call_executive_info()


def get_keyword_response(keyword, language):
    """Get specific response for selected keyword"""
    # Map translated keyword back to English for lookup
    keyword_mapping = get_keyword_mapping()
    english_keyword = keyword_mapping.get(keyword, keyword)

    responses = {
        "Voice Input Issues": {
            "English": "🎤 For voice input issues: 1) Check microphone permissions 2) Close other audio apps 3) Speak clearly 4) Try using Chrome browser. Need more help? 😊",
            "Hindi": "🎤 आवाज़ इनपुट की समस्याओं के लिए: 1) माइक्रोफ़ोन अनुमतियाँ जाँचें 2) अन्य ऑडियो ऐप बंद करें 3) स्पष्ट रूप से बोलें 4) Chrome ब्राउज़र का उपयोग करें। और मदद चाहिए? 😊",
        },
        "Database Questions": {
            "English": "📊 Our database contains policy, claims, and insured persons data. You can ask questions like 'How many policies are active?' or 'Show claims from Mumbai'. What would you like to know? 🤓",
            "Hindi": "📊 हमारे डेटाबेस में पॉलिसी, दावे और बीमित व्यक्तियों का डेटा है। आप 'कितनी पॉलिसियां सक्रिय हैं?' या 'मुंबई से सभी दावे दिखाएं' जैसे प्रश्न पूछ सकते हैं। आप क्या जानना चाहते हैं? 🤓",
        }
    }

    # Default response if keyword not found or language not available
    default_response = {
        "English": f"I'd be happy to help you with {keyword}! Could you please provide more details about your specific issue? 😊",
        "Hindi": f"मुझे {keyword} के साथ आपकी मदद करने में खुशी होगी! क्या आप कृपया अपनी विशिष्ट समस्या के बारे में और विवरण दे सकते हैं? 😊",
    }

    try:
        return responses.get(english_keyword, default_response).get(language, default_response["English"])
    except:
        return default_response.get(language, default_response["English"])


def show_call_executive_info():
    """Show customer executive contact information"""
    st.success("📞 **Customer Executive Contact Information**")

    col1, col2 = st.columns(2)

    with col1:
        st.info("""
        **📞 Phone Support:**
        • Toll Free: 1800-123-4567
        • Direct: +91-1234567219
        • Available: 9 AM - 9 PM (IST)
        """)

    with col2:
        st.info("""
        **💬 Other Support:**
        • Email: support@insuranceassist.com
        • WhatsApp: +91-1234567219
        • Live Chat: Available 24/7
        """)

    st.warning("⏰ **Current Status:** Our executives are available now! Average wait time: 2-3 minutes")

    # Callback request form
    st.markdown("### 📝 Request a Callback")

    with st.form("callback_form"):
        callback_name = st.text_input("Your Name:")
        callback_phone = st.text_input("Phone Number:")
        callback_issue = st.text_area("Brief description of your issue:")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            callback_submit = st.form_submit_button("📞 Request Callback", use_container_width=True)

    if callback_submit and callback_name and callback_phone:
        st.success(f"✅ **Callback requested successfully!**")
        st.info(f"Thank you {callback_name}! Our executive will call you at {callback_phone} within 15 minutes.")

        # Store callback request (in real app, this would go to a database)
        if "callback_requests" not in st.session_state:
            st.session_state.callback_requests = []

        st.session_state.callback_requests.append({
            "name": callback_name,
            "phone": callback_phone,
            "issue": callback_issue,
            "timestamp": datetime.datetime.now()
        })


def preprocess_voice_input(text):
    """Clean and preprocess voice input to make it more SQL-friendly"""
    if not text:
        return text

    # Convert to lowercase for processing
    text = text.lower().strip()

    # Common voice input corrections and removals
    corrections = {
        "to": "2", "too": "2", "two": "2",
        "for": "4", "four": "4", "fore": "4",
        "won": "1", "one": "1",
        "tree": "3", "three": "3",
        "ate": "8", "eight": "8",
        "nine": "9", "nein": "9",
        "how many": "count", "show me": "select", "give me": "select",
        "find": "select", "get": "select", "list": "select", "tell me": "select",
        "policies": "policy", "claims": "claim", "persons": "person",
        "um": "", "uh": "", "like": "", "you know": "", "please": "",
        "can you": "", "could you": "", "i want": "", "i need": "", "i would like": ""
    }

    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)

    text = " ".join(text.split())

    if text:
        text = text[0].upper() + text[1:]

    return text


def get_gemini_response(question, prompt):
    """Enhanced Gemini response with better error handling and preprocessing for the new database"""
    try:
        processed_question = preprocess_voice_input(question)
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content([prompt, processed_question])
        cleaned_response = response.text.strip().replace("```sql", "").replace("```", "").strip()
        cleaned_response = cleaned_response.replace("sql", "").replace("SQL", "").strip()

        # A simple validation to check for SQL keywords
        if not any(
                keyword in cleaned_response.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE']):
            return "SELECT 'I could not generate a valid SQL query. Please try rephrasing your question.' AS Error;"

        return cleaned_response
    except Exception as e:
        return f"SELECT 'An error occurred: {str(e)}' AS Error;"


def read_sql_query(sql, db_name="insurance_claims.db"):
    """Execute SQL query and return results and column names"""
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        column_names = [description[0] for description in cur.description] if cur.description else []
        conn.close()
        return rows, column_names
    except Exception as e:
        return [(f"Error executing query: {str(e)}",)], ["Error"]


def check_microphone_availability():
    """Check if microphone is available and not being used by other apps"""
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.1)
        return True, "Microphone available"
    except Exception as e:
        return False, f"❌ Could not access microphone: {str(e)}"


# The rest of the voice processing, audio file handling, and other utility functions
# from the original chatbot code remain largely the same.
# For brevity, they are not all repeated here but should be included in your final script.
# ... (speech_to_text_google_with_conflict_detection, process_audio_file, etc.)


# Updated prompt for the new insurance_claims.db
prompt = """
You are an expert in converting natural language questions into SQL queries for an insurance claims database.

Database Schema:
- POLICIES(policy_id, policy_type, policy_name, base_sum_insured, status)
- INSURED_PERSONS(insured_id, name, date_of_birth, gender, city, state, policy_id)
- CLAIMS(claim_id, policy_id, insured_id, coverage_id, status, claim_date, claim_amount, approved_amount, description)
- PREEXISTING_CONDITIONS(condition_id, insured_id, condition_name)
- COVERAGE_TYPES(coverage_id, coverage_name, description)

Instructions:
1.  Convert natural language to a valid SQLite query.
2.  Return ONLY the SQL query, no explanations.
3.  Join tables when necessary to answer the question. For example, to find claims by city, join CLAIMS and INSURED_PERSONS.
4.  Handle common questions about counts, sums, and filtering.

Examples:
- "How many policies are active?" -> SELECT COUNT(*) FROM POLICIES WHERE status = 'ACTIVE';
- "Show all claims from Mumbai" -> SELECT c.* FROM CLAIMS c JOIN INSURED_PERSONS ip ON c.insured_id = ip.insured_id WHERE ip.city = 'Mumbai';
- "List insured persons with 'Diabetes' as a pre-existing condition" -> SELECT ip.name, ip.city FROM INSURED_PERSONS ip JOIN PREEXISTING_CONDITIONS pc ON ip.insured_id = pc.insured_id WHERE pc.condition_name LIKE '%Diabetes%';
- "What is the total approved amount for all claims?" -> SELECT SUM(approved_amount) FROM CLAIMS;
"""

# Initialize session state variables
if "voice_input" not in st.session_state:
    st.session_state.voice_input = ""
if "use_voice_input" not in st.session_state:
    st.session_state.use_voice_input = False
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "voice_timeout" not in st.session_state:
    st.session_state.voice_timeout = 15
if "show_help" not in st.session_state:
    st.session_state.show_help = False
if "voice_auto_submit" not in st.session_state:
    st.session_state.voice_auto_submit = False
if "quick_query_submit" not in st.session_state:
    st.session_state.quick_query_submit = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "main"


def render_chatbot_main_page():
    """Renders the main page of the chatbot."""
    # Language selection at the top
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_language = st.selectbox(
            "🌍 Choose your preferred language:",
            ["English", "Hindi"],  # Simplified for brevity
            key="interface_language",
            index=["English", "Hindi"].index(st.session_state.user_language)
        )

        if selected_language != st.session_state.user_language:
            st.session_state.user_language = selected_language
            st.rerun()

    # Main Header
    st.markdown(f'<h1 class="main-title">{get_text("main_title")}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{get_text("subtitle")}</p>', unsafe_allow_html=True)

    # Main input section
    st.subheader(get_text("ask_question"))
    with st.form(key="question_form", clear_on_submit=False):
        question = st.text_input(
            "",
            value=st.session_state.get('voice_input', ''),
            placeholder=get_text("question_placeholder"),
            label_visibility="collapsed"
        )
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            enter_submitted = st.form_submit_button(get_text("submit"), type="primary", use_container_width=True)

    if st.session_state.get('use_voice_input', False):
        st.session_state.use_voice_input = False
        st.session_state.voice_input = ""

    submit = enter_submitted or st.session_state.get("voice_auto_submit", False) or st.session_state.get(
        "quick_query_submit", False)

    if submit and question:
        st.session_state.voice_auto_submit = False
        st.session_state.quick_query_submit = False
        with st.spinner(get_text("finding_answer")):
            sql_query = get_gemini_response(question, prompt)
            st.markdown("##### Generated SQL Query:")
            st.code(sql_query, language="sql")
            data, columns = read_sql_query(sql_query)

            st.subheader(get_text("results_found"))
            if data:
                df = pd.DataFrame(data, columns=columns)
                st.dataframe(df, use_container_width=True)
                st.success(get_text("found_results").format(count=len(data)))
            else:
                st.warning(get_text("no_results"))

    # Popular Questions
    st.subheader(get_text("popular_questions"))
    quick_queries = get_interface_translations()[st.session_state.user_language]["quick_queries"]
    cols = st.columns(2)
    for i, query in enumerate(quick_queries):
        with cols[i % 2]:
            if st.button(f"📝 {query}", key=f"quick_{i}"):
                st.session_state.voice_input = query
                st.session_state.use_voice_input = True
                st.session_state.quick_query_submit = True
                st.rerun()


# --- Page Rendering Functions ---

def render_document_processor_page():
    """Renders the main UI for the LLM Document Processing System."""
    st.markdown("<h1 style='text-align: center; color: #4B8BBE;'>📄 LLM Document Processing System</h1>",
                unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center;'>Upload policy documents, contracts, or emails and ask questions in natural language.</p>",
        unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ Controls")
        if st.button("💬 Go to Chatbot Assistant", use_container_width=True):
            st.session_state.current_page = "chatbot"
            st.rerun()

        st.markdown("---")
        st.subheader("1. Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload PDFs, Word docs, etc.",
            type=["pdf", "docx"],
            accept_multiple_files=True
        )

        if st.button("Process Documents", use_container_width=True, type="primary"):
            if uploaded_files:
                with st.spinner("Processing documents... This may take a moment."):
                    success = process_documents(uploaded_files)
                    if success:
                        st.success("Documents processed successfully! The system is ready for queries.")
                    else:
                        st.error("Failed to process documents. Please ensure files are valid and not empty.")
            else:
                st.warning("Please upload at least one document.")

    st.subheader("2. Ask a Question")
    query = st.text_input(
        "Enter your query:",
        placeholder="e.g., '46-year-old male, knee surgery in Pune, 3-month-old insurance policy'",
        help="Type your question about the uploaded documents here."
    )

    if st.button("Get Decision", use_container_width=True):
        if query:
            if not os.path.exists("faiss_vector_store.pkl"):
                st.error(
                    "You must process documents first. Please upload files and click 'Process Documents' in the sidebar.")
            else:
                with st.spinner("Analyzing query and searching documents..."):
                    result = process_query(query)
                    # ... (rest of the document processor display logic)


def render_chatbot_page():
    """Renders the integrated chatbot page."""
    with st.sidebar:
        st.title("⚙️ Navigation")
        if st.button("⬅️ Back to Document Processor", use_container_width=True):
            st.session_state.current_page = "main"
            st.rerun()

    if st.session_state.get("show_chat_page", False):
        show_chat_page()
    else:
        render_chatbot_main_page()


# --- Main App Router ---
if __name__ == "__main__":
    # Ensure the database is created and populated on first run
    if not os.path.exists("insurance_claims.db"):
        db_setup = InsuranceClaimsDatabase()
        db_setup.create_tables()
        db_setup.insert_sample_data()
        db_setup.close_connection()
        st.toast("Database has been initialized with sample data!")

    if "current_page" not in st.session_state:
        st.session_state.current_page = "main"

    if st.session_state.current_page == "main":
        render_document_processor_page()
    elif st.session_state.current_page == "chatbot":
        render_chatbot_page()