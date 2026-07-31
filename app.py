import streamlit as st
import yt_dlp
import os

# Import the algorithm modules we built
# from src.audio_utils import extract_audio_from_video, detect_volume_spikes
# from src.text_utils import analyze_and_extract
# from src.fusion import fuse_modalities

st.set_page_config(page_title="Virality Clip Extractor", layout="wide")

st.title("📹 Municipal Virality Extractor")
st.write("Upload a video or paste a YouTube link to automatically generate high-tension clips.")

# --- INGESTION OPTIONS ---
tab1, tab2 = st.tabs(["YouTube Link", "Upload File"])

video_path = None

with tab1:
    youtube_url = st.text_input("Paste YouTube URL:")
    if st.button("Process YouTube Video"):
        if youtube_url:
            st.info("Downloading video (this may take a moment for long meetings)...")
            # yt-dlp configuration to download the best quality mp4
            ydl_opts = {'format': 'best[ext=mp4]', 'outtmpl': 'data/raw_videos/downloaded_video.mp4'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            video_path = "data/raw_videos/downloaded_video.mp4"
            st.success("Download complete!")

with tab2:
    uploaded_file = st.file_uploader("Drop a .mov or .mp4 file here", type=['mp4', 'mov'])
    if uploaded_file is not None:
        video_path = os.path.join("data/raw_videos", uploaded_file.name)
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("File uploaded successfully!")

# --- PIPELINE EXECUTION ---
if video_path:
    st.divider()
    st.subheader("Running Algorithm...")
    
    with st.spinner("Extracting audio and transcribing..."):
        # Step 1: Extract Audio
        audio_path = video_path.replace(".mp4", ".wav").replace(".mov", ".wav").replace("raw_videos", "audio_wav")
        # extract_audio_from_video(video_path, audio_path)
        
        # Step 2: Analyze Data Tracks
        # text_clips = analyze_and_extract(audio_path)
        # audio_spikes = detect_volume_spikes(audio_path)
        
        # Step 3: Fuse and Score
        # final_ranked_clips = fuse_modalities(text_clips, audio_spikes)
        
        st.success("Analysis Complete!")
        
        # Mocking the output for the UI setup
        final_ranked_clips = [
            {"start": 120, "end": 185, "metrics": {"virality_score": 0.92}, "text": "This policy is an absolute failure and you know it!"},
            {"start": 3400, "end": 3450, "metrics": {"virality_score": 0.85}, "text": "Order! Order in the chamber!"}
        ]
        
    st.subheader("Top Viral Candidates")
    for i, clip in enumerate(final_ranked_clips):
        with st.expander(f"Clip {i+1} | Score: {clip['metrics']['virality_score']} | {clip['start']}s - {clip['end']}s"):
            st.write(f"**Transcript:** {clip['text']}")
            
            # Step 4: Render the actual video clip upon user request to save time
            if st.button(f"Generate Video for Clip {i+1}", key=f"btn_{i}"):
                st.info("FFmpeg is cutting the video. Please wait...")
                # Call your utils/clip_generator.py here
                # st.video("path_to_final_clip.mp4")