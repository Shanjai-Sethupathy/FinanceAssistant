import streamlit as st  
import requests  
import base64  
import sounddevice as sd  
import soundfile as sf  
import io  

# Backend URL  
BACKEND_URL = "http://localhost:8000/orchestrate/"  

# Streamlit App Title  
st.title("🔊 Voice & Text Agent Interface")  

# Recording parameters  
SAMPLE_RATE = 16000  # Whisper preferred sample rate  
DURATION = 5  # seconds  

# Section: Text Input  
st.subheader("🔹 Text Query")  
user_text = st.text_area("Enter your text query:")  

# Section: Voice Input  
st.subheader("🔹 Voice Query")  
if st.button("🎤 Record Voice (5 seconds)"):  
    st.info("Recording... Please speak now.")  
    # Record audio  
    recording = sd.rec(int(SAMPLE_RATE * DURATION), samplerate=SAMPLE_RATE, channels=1, dtype='int16')  
    sd.wait()  
    st.success("Recording complete!")  

    # Save to WAV in memory  
    audio_io = io.BytesIO()  
    sf.write(audio_io, recording, SAMPLE_RATE, format='WAV')  
    audio_bytes = audio_io.getvalue()  

    # Encode in base64 for transport  
    encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')  

    # Send to backend API  
    with st.spinner("Sending voice query to the backend..."):  
        try:  
            response = requests.post(  
                BACKEND_URL,  
                json={"audio_data": encoded_audio, "query": ""}   
            )  
            if response.status_code == 200:  
                answer = response.json().get("response", "No response received.")  
                st.text_area("🤖 Response:", answer, height=150)  
            else:  
                st.error(f"Error: {response.status_code}")  
        except Exception as e:  
            st.error(f"Error communicating with backend: {e}")  

# Process Text Query  
if user_text:  
    if st.button("💬 Send Text Query"):  
        with st.spinner("Sending text query..."):  
            try:  
                response = requests.post(  
                    BACKEND_URL,  
                    json={"audio_data": "", "query": user_text}  
                )  
                if response.status_code == 200:  
                    answer = response.json().get("response", "No response received.")  
                    st.text_area("🤖 Response:", answer, height=150)  
                else:  
                    st.error(f"Error: {response.status_code}")  
            except Exception as e:  
                st.error(f"Error communicating with backend: {e}") 