import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="Municipal Virality Extractor", layout="wide")

# --- HELPER FUNCTIONS ---
def format_timestamp(seconds):
    """Converts seconds into HH:MM:SS format for video editors."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{secs:02}"
    return f"{minutes:02}:{secs:02}"

st.title("📹 Municipal Virality Extractor")
st.write("Upload a video or paste a YouTube link to identify high-tension moments and timestamps.")

tab1, tab2 = st.tabs(["YouTube Link", "Upload File"])
video_path = None

with tab1:
    youtube_url = st.text_input("Paste YouTube URL:")
    if st.button("Process YouTube Video"):
        if youtube_url:
            st.info("Downloading video...")
            ydl_opts = {'format': 'best[ext=mp4]', 'outtmpl': 'downloaded_video.mp4'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            video_path = "downloaded_video.mp4"
            st.success("Download complete!")

with tab2:
    uploaded_file = st.file_uploader("Drop a .mov or .mp4 file here", type=['mp4', 'mov'])
    if uploaded_file is not None:
        video_path = uploaded_file.name
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("File uploaded successfully!")

# --- PIPELINE EXECUTION ---
if video_path:
    st.divider()
    
    num_clips = st.slider("Number of viral candidate clips to output:", min_value=5, max_value=20, value=10)
    
    st.subheader("Running Algorithm...")
    
    with st.spinner("Extracting audio, scoring tension, and generating timestamps..."):
        # Real pipeline steps (uncomment when running with full models):
        # audio_path = video_path.replace(".mp4", ".wav").replace(".mov", ".wav")
        # extract_audio_from_video(video_path, audio_path)
        # text_clips = analyze_and_extract(audio_path)
        # audio_spikes = detect_volume_spikes(audio_path)
        # final_ranked_clips = fuse_modalities(text_clips, audio_spikes)[:num_clips]
        
        # Simulated data output for testing:
        mock_clips = [
            {
                "start": 120, 
                "end": 185, 
                "duration": 65,
                "metrics": {"virality_score": 0.92, "text_tension": 0.95, "audio_energy": 0.88}, 
                "text": "This policy is an absolute failure and you know it! We have watched budget deficits climb for three consecutive quarters while essential public services get slashed. The public deserves transparency right now."
            },
            {
                "start": 3400, 
                "end": 3450, 
                "duration": 50,
                "metrics": {"virality_score": 0.85, "text_tension": 0.89, "audio_energy": 0.81}, 
                "text": "Order! Order in the chamber! If the gallery cannot maintain composure during public comment, I will direct security to clear the room immediately."
            },
            {
                "start": 4120, 
                "end": 4190, 
                "duration": 70,
                "metrics": {"virality_score": 0.78, "text_tension": 0.82, "audio_energy": 0.74}, 
                "text": "I yield my time to the gentleman from the third district, but let the record reflect that the council refused to answer the audit questions raised during open session."
            },
            {
                "start": 5000, 
                "end": 5040, 
                "duration": 40,
                "metrics": {"virality_score": 0.72, "text_tension": 0.75, "audio_energy": 0.69}, 
                "text": "Are you out of your mind? That budget projection is completely fabricated and does not reflect actual municipal expenditures from last fiscal year!"
            },
            {
                "start": 6200, 
                "end": 6260, 
                "duration": 60,
                "metrics": {"virality_score": 0.68, "text_tension": 0.70, "audio_energy": 0.66}, 
                "text": "We need to pause proceedings and clear the floor. We are taking a fifteen-minute emergency recess while council meets in closed session."
            }
        ]
        final_ranked_clips = mock_clips[:num_clips]
        
        st.success("Analysis Complete!")
        
    st.subheader(f"Top {len(final_ranked_clips)} High-Tension Moments")
    
    for i, clip in enumerate(final_ranked_clips):
        start_tc = format_timestamp(clip['start'])
        end_tc = format_timestamp(clip['end'])
        
        with st.expander(f"📌 Clip #{i+1} | {start_tc} ➔ {end_tc} (Duration: {clip['duration']}s) | Virality Score: {clip['metrics']['virality_score']}"):
            
            # Key Information Bar
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Start Timecode", start_tc)
            col2.metric("End Timecode", end_tc)
            col3.metric("Raw Seconds", f"{clip['start']}s - {clip['end']}s")
            col4.metric("Virality Score", clip['metrics']['virality_score'])
            
            st.divider()
            
            # Full Transcript Block
            st.write("**Full Clip Transcript:**")
            st.text_area(
                label="Copy Transcript", 
                value=clip['text'], 
                height=100, 
                key=f"transcript_{i}"
            )
            
            # Copy-paste helper string for NLE markers/notes
            st.code(f"IN: {start_tc} | OUT: {end_tc} | SCORE: {clip['metrics']['virality_score']}", language="text")
