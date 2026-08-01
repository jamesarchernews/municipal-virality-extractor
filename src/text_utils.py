import whisper_timestamped as whisper
from transformers import pipeline

print("Loading Whisper model...")
audio_model = whisper.load_model("base") 

print("Loading Zero-Shot Classification model...")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Journalistic themes to capture both tense and civic governance moments
NEWSWORTHY_THEMES = [
    "heated debate", 
    "public outcry", 
    "accusation", 
    "resignation or firing",
    "budget presentation or financial dispute",
    "reading of a staff report or resolution",
    "official statement by a council member",
    "public comment period",
    "demonstration or presentation to the board",
    "voting on an agenda item or motion",
    "awarding of a city contract"
]

def analyze_and_extract(audio_path, min_clip_duration=30, max_clip_duration=90):
    print(f"Transcribing {audio_path}...")
    result = whisper.transcribe(audio_model, audio_path, language="en")
    sentences = result['segments']
    viral_candidates = []
    
    print("Scoring sentences for civic and newsworthy themes...")
    for segment in sentences:
        text = segment['text'].strip()
        if not text or len(text.split()) < 5: 
            continue # Skip short filler phrases
        
        classification = classifier(text, NEWSWORTHY_THEMES)
        top_theme = classification['labels'][0]
        top_score = classification['scores'][0]
        
        # Lowered threshold (0.50) to catch quiet, structural civic moments
        if top_score > 0.50:
            segment['tension_score'] = top_score
            segment['primary_theme'] = top_theme
            viral_candidates.append(segment)

    print("Building dynamic clips...")
    final_clips = build_dynamic_clips(sentences, viral_candidates, min_clip_duration, max_clip_duration)
    return final_clips

def build_dynamic_clips(all_segments, candidates, min_dur, max_dur):
    clips = []
    for candidate in candidates:
        start_time = candidate['start']
        end_time = candidate['end']
        clip_text = candidate['text']
        
        idx = next((i for i, seg in enumerate(all_segments) if seg['id'] == candidate['id']), -1)
        if idx == -1: continue
        
        back_idx = idx - 1
        while back_idx >= 0 and (end_time - all_segments[back_idx]['start']) < max_dur:
            if (start_time - all_segments[back_idx]['start']) > 15:
                break
            start_time = all_segments[back_idx]['start']
            clip_text = all_segments[back_idx]['text'] + " " + clip_text
            back_idx -= 1
            
        forward_idx = idx + 1
        while forward_idx < len(all_segments) and (all_segments[forward_idx]['end'] - start_time) <= max_dur:
            end_time = all_segments[forward_idx]['end']
            clip_text = clip_text + " " + all_segments[forward_idx]['text']
            forward_idx += 1
            
        duration = end_time - start_time
        if duration >= min_dur:
            clips.append({
                "start": round(start_time, 2),
                "end": round(end_time, 2),
                "duration": round(duration, 2),
                "text": clip_text,
                "anchor_tension_score": candidate['tension_score'],
                "theme": candidate['primary_theme']
            })
            
    return deduplicate_clips(clips)

def deduplicate_clips(clips):
    clips.sort(key=lambda x: x['anchor_tension_score'], reverse=True)
    unique_clips = []
    for clip in clips:
        overlap = False
        for u_clip in unique_clips:
            if max(0, min(clip['end'], u_clip['end']) - max(clip['start'], u_clip['start'])) > 10:
                overlap = True
                break
        if not overlap:
            unique_clips.append(clip)
    return unique_clips
