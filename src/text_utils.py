import whisper_timestamped as whisper
from transformers import pipeline

print("Loading Whisper model...")
audio_model = whisper.load_model("base") 

print("Loading Zero-Shot Classification model...")
# Swapped to a zero-shot classifier to detect specific newsworthy themes
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define the exact themes that make a municipal moment "newsworthy" for your journalism
NEWSWORTHY_THEMES = [
    "heated debate", 
    "public outcry", 
    "policy disagreement", 
    "official statement", 
    "accusation", 
    "resignation or firing",
    "budget dispute"
]

def analyze_and_extract(audio_path, min_clip_duration=30, max_clip_duration=90):
    print(f"Transcribing {audio_path}...")
    result = whisper.transcribe(audio_model, audio_path, language="en")
    sentences = result['segments']
    viral_candidates = []
    
    print("Scoring sentences for newsworthy themes...")
    for segment in sentences:
        text = segment['text'].strip()
        if not text or len(text.split()) < 5: 
            continue # Skip very short phrases like "Thank you."
        
        # The model checks if the sentence aligns with any of our defined themes
        classification = classifier(text, NEWSWORTHY_THEMES)
        top_theme = classification['labels'][0]
        top_score = classification['scores'][0]
        
        # If the sentence strongly matches a newsworthy theme (score > 0.60)
        if top_score > 0.60:
            segment['tension_score'] = top_score
            segment['primary_theme'] = top_theme
            viral_candidates.append(segment)

    print("Building dynamic clips...")
    final_clips = build_dynamic_clips(sentences, viral_candidates, min_clip_duration, max_clip_duration)
    return final_clips

def build_dynamic_clips(all_segments, candidates, min_dur, max_dur):
    # (Keep the exact same build_dynamic_clips and deduplicate_clips logic from before here)
    # They still work perfectly for windowing the context.
    pass # Re-paste the windowing code here
