from pathlib import Path
from openai import OpenAI
import textwrap
from tqdm import tqdm  # Import tqdm for the loading bar
from dotenv import load_dotenv
import os
load_dotenv()
openai_api_key = os.environ["OPENAI_API_KEY"]
print(f"OpenAI API Key: {'Loaded' if openai_api_key else 'Not Loaded'}")

client = OpenAI()

# Define the paths
base_path = Path(__file__).parent
speech_file_path = base_path / input("Desired File Name (ex. chapter.mp3): ")
text_file_path = base_path / input("Full Path of .txt script: ")

# Read the text from the .txt file
with open(text_file_path, 'r', encoding='utf-8') as file:
    text_to_speak = file.read()

# Maximum characters allowed per request
max_chars = 4096


# Function to split text into chunks
def split_text(text, max_length):
    return textwrap.wrap(text, max_length)


# Split the text into manageable chunks
text_chunks = split_text(text_to_speak, max_chars)

# List to hold paths of the audio chunk files
audio_files = []

# Process each chunk individually with a loading bar
for idx, chunk in enumerate(tqdm(text_chunks, desc="Processing text chunks")):
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=chunk
        )

        # Save each audio chunk to a temporary file
        chunk_file_path = base_path / f"speech_chunk_{idx}.mp3"
        response.stream_to_file(chunk_file_path)
        audio_files.append(chunk_file_path)
    except Exception as e:
        print(f"An error occurred while processing chunk {idx}: {e}")

# Combine the audio chunks into one file
from pydub import AudioSegment

# Ensure pydub and ffmpeg are installed
# You can install pydub using: pip install pydub
# ffmpeg installation varies by system

combined_audio = AudioSegment.empty()

# Add a loading bar for combining audio files
for file in tqdm(audio_files, desc="Combining audio files"):
    audio = AudioSegment.from_file(file)
    combined_audio += audio

# Export the combined audio file
combined_audio.export(speech_file_path, format="mp3")

# Optionally, delete the temporary chunk files
for file in audio_files:
    os.remove(file)
