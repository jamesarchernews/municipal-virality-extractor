import whisper_timestamped as whisper
from transformers import pipeline

audio_model = whisper.load_model("base") 
sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")

def analyze_and_extract(audio_path, min_clip_duration=30, max_clip_duration=90):
    result = whisper.transcribe(audio_model, audio_path, language="en")
    sentences = result['segments']
    viral_candidates = []
    
    for segment in sentences:
        text = segment['text'].strip()
        if not text: continue
        
        sentiment = sentiment_analyzer(text)[0]
        if sentiment['label'] == 'negative' and sentiment['score'] > 0.75:
            segment['tension_score'] = sentiment['score']
            viral_candidates.append(segment)

    return build_dynamic_clips(sentences, viral_candidates, min_clip_duration, max_clip_duration)

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
                "anchor_tension_score": candidate['tension_score']
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
