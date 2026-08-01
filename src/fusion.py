def normalize_audio_spikes(audio_spikes):
    if not audio_spikes:
        return []
    max_energy = max(spike['max_energy'] for spike in audio_spikes)
    for spike in audio_spikes:
        spike['normalized_energy'] = spike['max_energy'] / max_energy if max_energy > 0 else 0.0
    return audio_spikes

def fuse_modalities(text_clips, raw_audio_spikes):
    audio_spikes = normalize_audio_spikes(raw_audio_spikes)
    fused_clips = []
    
    for clip in text_clips:
        clip_start = clip['start']
        clip_end = clip['end']
        theme = clip.get('theme', '')
        
        overlapping_spikes = [s for s in audio_spikes if s['start'] <= clip_end and s['end'] >= clip_start]
        audio_score = max((s['normalized_energy'] for s in overlapping_spikes), default=0.0)
        text_score = clip['anchor_tension_score']
        
        # Heavy text weighting for quiet civic moments, split weighting for loud arguments
        if theme in ["heated debate", "public outcry", "accusation"]:
            virality_score = (text_score * 0.5) + (audio_score * 0.5)
        else:
            virality_score = (text_score * 0.9) + (audio_score * 0.1)
        
        fused_clips.append({
            "start": clip_start,
            "end": clip_end,
            "duration": clip['duration'],
            "text": clip['text'],
            "theme": theme,
            "metrics": {
                "text_score": round(text_score, 3),
                "audio_energy": round(audio_score, 3),
                "virality_score": round(virality_score, 3)
            }
        })
        
    fused_clips.sort(key=lambda x: x['metrics']['virality_score'], reverse=True)
    return fused_clips
