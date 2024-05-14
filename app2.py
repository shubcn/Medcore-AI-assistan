import pyaudio
import wave
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

# Set recording parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5  # Change this value to adjust the recording duration

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open a stream for recording
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Recording...")

# Create an empty list to store the recorded frames
frames = []

# Record audio for the specified duration
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Finished recording.")

# Stop and close the stream
stream.stop_stream()
stream.close()
p.terminate()

# Save the recorded audio as a WAV file
output_file = "recorded_audio.wav"
wf = wave.open(output_file, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

print(f"Audio saved to {output_file}")

KEY = os.environ.get("API_KEY")


client = OpenAI(api_key=KEY)
audio_file = open(f"{output_file}", "rb")
transcription = client.audio.transcriptions.create(
  model="whisper-1",
  file=audio_file,
  response_format="text"
)
print(transcription)