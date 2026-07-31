import librosa
import numpy as np
import subprocess

def extract_audio_from_video(video_path, output_audio_path):
    print(f"Extracting audio to {output_audio_path}...")
    command = [
        "ffmpeg", "-i", video_path, 
        "-q:a", "0", "-map", "a", 
        output_audio_path, "-y"
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Audio extraction complete.")

def detect_volume_spikes(audio_path, threshold_multiplier=2.5):
    print(f"Loading audio from {audio_path}...")
    y, sr = librosa.load(audio_path, sr=16000)
    
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=512)
    
    mean_rms = np.mean(rms)
    std_rms = np.std(rms)
    threshold = mean_rms + (threshold_multiplier * std_rms)
    
    spikes = []
    is_spiking = False
    spike_start = 0
    
    for i, energy in enumerate(rms):
        if energy > threshold:
            if not is_spiking:
                is_spiking = True
                spike_start = times[i]
        else:
            if is_spiking:
                is_spiking = False
                spike_end = times[i]
                
                if (spike_end - spike_start) > 0.5:
                    spikes.append({
                        "start": round(spike_start, 2),
                        "end": round(spike_end, 2),
                        "duration": round(spike_end - spike_start, 2),
                        "max_energy": float(np.max(rms[int(spike_start*sr/512):i]))
                    })
                    
    return spikes
