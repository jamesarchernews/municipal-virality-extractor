import streamlit as st
import yt_dlp
import os
import uuid # For generating unique IDs for each processed video

st.set_page_config(page_title="Municipal Virality Dashboard", layout="wide")

# --- INITIALIZE SESSION STATE ---
# This is the crucial step that creates your "Library"
# It remembers videos and clips even if you upload a new one
if 'video_library' not in st.session_state:
    st.session_state.video_library = []

# --- HELPER FUNCTIONS ---
def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{secs:02}"
    return f"{minutes:02}:{secs:02}"

def add_to_library(title, clips):
    """Saves the processed video and its clips to the permanent session state."""
    st.session_state.video_library.insert(0, {
        "id": str(uuid.uuid4()),
        "title": title,
        "clips": clips
    })

# --- UI: SIDEBAR FOR UPLOADS ---
with st.sidebar:
    st.header("📤 Add New Video")
    
    # Notice the slider is now on the sidebar, accessible BEFORE processing!
    num_clips = st.slider("Number of viral clips to find:", min_value=5, max_value=20, value=10)
    
    tab1, tab2 = st.tabs(["YouTube Link", "Upload File"])
    new_video_path = None
    video_title = "Untitled Municipal Meeting"

    with tab1:
        youtube_url = st.text_input("Paste YouTube URL:")
        if st.button("Process YouTube Video"):
            if youtube_url:
                with st.spinner("Downloading video..."):
                    ydl_opts = {'format': 'best[ext=mp4]', 'outtmpl': 'data/downloaded_video.mp4'}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info_dict = ydl.extract_info(youtube_url, download=True)
                        video_title = info_dict.get('title', 'YouTube Video')
                    new_video_path = "data/downloaded_video.mp4"

    with tab2:
        uploaded_file = st.file_uploader("Drop a .mov or .mp4 file here", type=['mp4', 'mov'])
        if uploaded_file is not None:
            if st.button("Process Uploaded File"):
                new_video_path = uploaded_file.name
                video_title = uploaded_file.name
                with open(new_video_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

    # --- PIPELINE EXECUTION ---
    if new_video_path:
        with st.spinner("Scanning for newsworthy moments..."):
            # NOTE: In a live environment, you would call your actual models here.
            # final_ranked_clips = fuse_modalities(text_clips, audio_spikes)[:num_clips]
            
            # Simulated data for the dashboard layout
            mock_clips = [
                 {
                    "start": 120, "end": 185, "duration": 65,
                    "metrics": {"virality_score": 0.92}, 
                    "theme": "Policy Disagreement",
                    "text": "This policy is an absolute failure and you know it! We have watched budget deficits climb for three consecutive quarters..."
                },
                {
                    "start": 3400, "end": 3450, "duration": 50,
                    "metrics": {"virality_score": 0.85}, 
                    "theme": "Public Outcry",
                    "text": "Order! Order in the chamber! If the gallery cannot maintain composure during public comment, I will direct security to clear the room immediately."
                }
            ]
            
            # Save the results to the library!
            add_to_library(video_title, mock_clips[:num_clips])
            st.success("Added to Dashboard!")

# --- UI: MAIN DASHBOARD GALLERY ---
st.title("📼 Your Videos")

if len(st.session_state.video_library) == 0:
    st.info("Your library is empty. Use the sidebar to upload a municipal meeting.")
else:
    # Build the Grid Layout
    cols = st.columns(3) # Creates a 3-column grid for the video thumbnails
    
    for idx, video_data in enumerate(st.session_state.video_library):
        col = cols[idx % 3] # Distributes the videos evenly across the 3 columns
        
        with col:
            # Create a card-like container for each video
            with st.container(border=True):
                st.subheader(f"🏛️ {video_data['title'][:30]}...")
                st.write(f"**{len(video_data['clips'])} Clips Generated**")
                
                # When clicked, it displays the clips for THIS specific video
                with st.expander("View Extracted Clips"):
                    for i, clip in enumerate(video_data['clips']):
                        start_tc = format_timestamp(clip['start'])
                        end_tc = format_timestamp(clip['end'])
                        
                        st.markdown(f"### Clip #{i+1}: {clip.get('theme', 'Highlight')}")
                        st.write(f"**Score:** {clip['metrics']['virality_score']} | **Length:** {clip['duration']}s")
                        
                        st.text_area("Transcript:", value=clip['text'], height=100, key=f"trans_{video_data['id']}_{i}")
                        st.code(f"IN: {start_tc} | OUT: {end_tc}", language="text")
                        st.divider()
