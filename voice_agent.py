import threading  
import io  
import logging  
import sounddevice as sd  
import numpy as np  
import soundfile as sf  # Make sure to install via: pip install soundfile  

# Make sure to have whisper and pyttsx3 installed  
try:  
    import whisper  
except ImportError:  
    whisper = None  

try:  
    import pyttsx3  
except ImportError:  
    pyttsx3 = None  

logger = logging.getLogger(__name__)  

class VoiceAgent:  
    def __init__(self, stt_model="base", tts_engine="default", llm_callback=None):  
        if whisper is None:  
            raise ImportError("Whisper is required for STT.")  
        if pyttsx3 is None:  
            raise ImportError("pyttsx3 is required for TTS.")  
        self.stt_model = whisper.load_model(stt_model)  
        self.tts_engine = pyttsx3.init()  
        self.llm_callback = llm_callback  
        self.speaking_event = threading.Event()  

    def transcribe_audio(self, audio_data: bytes) -> str:  
        try:  
            with io.BytesIO(audio_data) as audio_file:  
                result = self.stt_model.transcribe(audio_file)  
            text = result["text"].strip()  
            logger.info(f"Transcribed text: {text}")  
            return text  
        except Exception as e:  
            logger.error(f"Error transcribing audio: {e}")  
            return ""  

    def speak_text(self, text: str):  
        def _speak():  
            self.speaking_event.clear()  
            try:  
                self.tts_engine.say(text)  
                self.tts_engine.runAndWait()  
            except Exception as e:  
                logger.error(f"TTS Error: {e}")  
            finally:  
                self.speaking_event.set()  
        threading.Thread(target=_speak).start()  

    def listen_microphone(self, duration=5, sample_rate=16000, channels=1) -> bytes:  
        try:  
            logger.info("Listening...")  
            audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype=np.int16)  
            sd.wait()  
            logger.info("Recording complete.")  
            with io.BytesIO() as buffer:  
                # Write WAV data directly to BytesIO using soundfile  
                sf.write(buffer, audio, sample_rate, format='WAV')  
                return buffer.getvalue()  
        except Exception as e:  
            logger.error(f"Error recording audio: {e}")  
            return b""  

    def process_microphone_input(self, duration=5):  
        audio_data = self.listen_microphone(duration=duration)  
        if audio_data:  
            text = self.transcribe_audio(audio_data)  
            if text:  
                response = self.llm_callback(text) if self.llm_callback else f"You said: {text}"  
                self.speak_text(response)  

# Example usage  
if __name__ == "__main__":  
    def dummy_llm_callback(text: str) -> str:  
        return f"Echoing: {text} (LLM response)"  

    agent = VoiceAgent(stt_model="base", tts_engine="default", llm_callback=dummy_llm_callback)  
    agent.process_microphone_input(duration=5)  