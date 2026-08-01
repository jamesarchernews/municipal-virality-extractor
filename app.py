import streamlit as st
import yt_dlp
import os
import uuid

from src.audio_utils import extract_audio_from_video, detect_volume_spikes
from src.text_utils import analyze_and_extract
from src.fusion import fuse_modalities

st.set_page_config(page_title="Municipal Virality Dashboard", layout="wide")

# Persistent Video Library State
if 'video_library' not in st.session_state:
    st.session_state.video_library = []

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{secs:02}"
    return f"{minutes:02}:{secs:02}"

def add_to_library(title, clips):
    st.session_state.video_library.insert(0, {
        "id": str(uuid.uuid4()),
        "title": title,
        "clips": clips
    })

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Controls & Upload")
    num_clips = st.slider("Clips to generate per video:", min_value=5, max_value=20, value=10)
    
    tab1, tab2 = st.tabs(["YouTube Link", "Upload File"])
    new_video_path = None
    video_title = "Municipal Meeting"

    with tab1:
        youtube_url = st.text_input("YouTube URL:")
        if st.button("Process YouTube Link"):
            if youtube_url:
                with st.spinner("Downloading..."):
                    os.makedirs("data", exist_ok=True)
                    ydl_opts = {'format': 'best[ext=mp4]', 'outtmpl': 'data/downloaded_video.mp4'}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(youtube_url, download=True)
                        video_title = info.get('title', 'YouTube Video')
                    new_video_path = "data/downloaded_video.mp4"

    with tab2:
        uploaded_file = st.file_uploader("Drop .mp4 or .mov file", type=['mp4', 'mov'])
        if uploaded_file is not None:
            if st.button("Process Uploaded Video"):
                os.makedirs("data", exist_ok=True)
                new_video_path = os.path.join("data", uploaded_file.name)
                video_title = uploaded_file.name
                with open(new_video_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

    if new_video_path:
        with st.spinner("Analyzing audio, text, and civic themes..."):
            audio_path = new_video_path.rsplit('.', 1)[0] + ".wav"
            extract_audio_from_video(new_video_path, audio_path)
            text_clips = analyze_and_extract(audio_path)
            audio_spikes = detect_volume_spikes(audio_path)
            final_ranked_clips = fuse_modalities(text_clips, audio_spikes)[:num_clips]
            
            add_to_library(video_title, final_ranked_clips)
            st.success("Analysis Complete! Added to library.")

# --- MAIN DASHBOARD GALLERY ---
st.title("🏛️ Municipal Video Library")

if len(st.session_state.video_library) == 0:
    st.info("No videos processed yet. Set your clip count on the sidebar and upload a video.")
else:
    cols = st.columns(2)
    for idx, video_data in enumerate(st.session_state.video_library):
        col = cols[idx % 2]
        with col:
            with st.container(border=True):
                st.subheader(f"📹 {video_data['title']}")
                st.write(f"**Total Clips Extracted:** {len(video_data['clips'])}")
                
                with st.expander("View Timestamps & Transcripts"):
                    for i, clip in enumerate(video_data['clips']):
                        start_tc = format_timestamp(clip['start'])
                        end_tc = format_timestamp(clip['end'])
                        theme = clip.get('theme', 'General Highlight').title()
                        
                        st.markdown(f"#### Clip #{i+1}: {theme}")
                        st.write(f"**Score:** {clip['metrics']['virality_score']} | **Duration:** {clip['duration']}s")
                        st.write(f"**Timecode:** `{start_tc}` ➔ `{end_tc}` ({clip['start']}s - {clip['end']}s)")
                        
                        st.text_area("Full Transcript:", value=clip['text'], height=90, key=f"tr_{video_data['id']}_{i}")
                        st.code(f"IN: {start_tc} | OUT: {end_tc} | THEME: {theme}", language="text")
                        st.divider()
