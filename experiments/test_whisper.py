import whisper

# Load Whisper model
model = whisper.load_model("base")

# Path to ONE audio file
audio_path = r"C:\Users\likhi\Audio_Dataset\data\audio\caller\00d676d7058c49bb.wav"

# Transcribe
result = model.transcribe(audio_path)

# Print output
print("Transcription:")
print(result["text"])
