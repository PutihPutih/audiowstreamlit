import streamlit as st
import pyaudio
import wave
import librosa
import numpy as np
import soundfile as sf

# Function to record audio
def record_audio(filename, duration=5, rate=44100, chunk=1024):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=chunk)
    frames = []

    for _ in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

# Function to load audio
def load_audio(filename):
    audio_data, sr = librosa.load(filename, sr=None)
    return audio_data, sr

# Function to apply pitch shift
def pitch_shift(audio_data, sr, n_steps):
    return librosa.effects.pitch_shift(y=audio_data, sr=sr, n_steps=n_steps)

# Function to change volume
def change_volume(audio_data, gain_dB):
    return audio_data * (10**(gain_dB / 20))

# Function to apply time stretch
def time_stretch(audio_data, rate):
    return librosa.effects.time_stretch(y=audio_data, rate=rate)

# Function to save the processed audio
def save_audio(filename, audio_data, sr):
    sf.write(filename, audio_data, sr)

# Streamlit UI for the app
st.title('Audio Processing Web App')

# Use session state to store original and processed audio data
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
    st.session_state.sr = None
    st.session_state.processed_audio = None
    st.session_state.original_audio = None  # Store original audio for reset

# Record audio section
if st.button('Record Audio'):
    st.write("Recording audio for 5 seconds...")
    record_audio('output.wav', duration=5)
    st.write("Recording complete! Audio saved as 'output.wav'.")

# Upload audio file section
uploaded_file = st.file_uploader("Choose an audio file", type=["wav"])
if uploaded_file is not None:
    with open('uploaded.wav', 'wb') as f:
        f.write(uploaded_file.getbuffer())
    st.write("Audio file uploaded successfully!")
    st.session_state.audio_data, st.session_state.sr = load_audio('uploaded.wav')
    st.session_state.original_audio = st.session_state.audio_data  # Save original audio

# Load the recorded or uploaded audio file
if st.button('Load Audio'):
    if uploaded_file is not None:
        st.session_state.audio_data, st.session_state.sr = load_audio('uploaded.wav')
        st.session_state.original_audio = st.session_state.audio_data  # Save original audio
    else:
        st.session_state.audio_data, st.session_state.sr = load_audio('output.wav')
        st.session_state.original_audio = st.session_state.audio_data  # Save original audio
    st.write("Audio loaded successfully!")

# Ensure audio is loaded before applying effects
if st.session_state.audio_data is not None:
    # Choose an effect to apply
    effect = st.selectbox('Choose an effect to apply:', ('Pitch Shift', 'Volume Change', 'Time Stretch'))

    if effect == 'Pitch Shift':
        n_steps = st.slider('Choose pitch shift (in semitones)', -12, 12, 0)
        if st.button('Apply Pitch Shift'):
            st.session_state.processed_audio = pitch_shift(st.session_state.audio_data, st.session_state.sr, n_steps=n_steps)
            save_audio('processed_audio.wav', st.session_state.processed_audio, st.session_state.sr)
            st.write("Pitch shift applied and saved!")

    elif effect == 'Volume Change':
        gain_dB = st.slider('Choose volume gain (dB)', -20, 20, 0)
        if st.button('Apply Volume Change'):
            st.session_state.processed_audio = change_volume(st.session_state.audio_data, gain_dB=gain_dB)
            save_audio('processed_audio.wav', st.session_state.processed_audio, st.session_state.sr)
            st.write("Volume changed and saved!")

    elif effect == 'Time Stretch':
        rate = st.slider('Choose stretch rate', 0.5, 2.0, 1.0)
        if st.button('Apply Time Stretch'):
            st.session_state.processed_audio = time_stretch(st.session_state.audio_data, rate=rate)
            save_audio('processed_audio.wav', st.session_state.processed_audio, st.session_state.sr)
            st.write("Time stretch applied and saved!")

    # Add Play Processed Audio button
    if st.session_state.processed_audio is not None:
        if st.button('Play Processed Audio'):
            audio_file = open('processed_audio.wav', 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/wav')

    # Add Reset button to revert back to original audio
    if st.button('Reset Audio'):
        st.session_state.processed_audio = st.session_state.original_audio
        save_audio('processed_audio.wav', st.session_state.processed_audio, st.session_state.sr)
        st.write("Audio reset to original.")
        audio_file = open('processed_audio.wav', 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/wav')

else:
    st.write("Please load an audio file before applying effects.")
