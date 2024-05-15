import pyaudio
import wave
from openai import OpenAI
import os
from dotenv import load_dotenv
import pygame
load_dotenv()

def play_mp3(file_path):
    # Initialize pygame
    pygame.init()

    try:
        # Load the MP3 file
        pygame.mixer.music.load(file_path)
        
        # Play the MP3 file
        pygame.mixer.music.play()

        # Wait until the MP3 finishes playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
    except pygame.error:
        print("Error: Unable to load or play the MP3 file.")
    
    finally:
        # Quit pygame
        pygame.quit()

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

#STT--------------------------------------------
client = OpenAI(api_key=KEY)
audio_file = open(f"{output_file}", "rb")
transcription = client.audio.transcriptions.create(
  model="whisper-1",
  file=audio_file,
  response_format="text"
)
print("User: ",transcription)

#LLM-----------------------------------------------------------

completion = client.chat.completions.create(
    model='gpt-4-0125-preview',
    messages=[
        {"role": "system", "content": "Act like chatbot"},
        {"role": "user", "content": f'{transcription}'}
    ]
    )

result = completion.choices[0].message.content
print("Medcore:",result)

#TTS
speech_file_path =  "ai_reply.mp3"
response = client.audio.speech.create(
  model="tts-1",
  voice="nova",
  input=result
  )

response.stream_to_file(speech_file_path)

play_mp3(speech_file_path)





