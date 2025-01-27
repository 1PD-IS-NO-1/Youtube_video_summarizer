import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

# Google Gemini API Key
GOOGLE_API_KEY = os.getenv("PASTE API kEY ON HERE")
# Configure Google Gemini with your API key
genai.configure(api_key="PASTE API KEY ON HERE")

# Create a GenerativeModel instance
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_prompt(word_count):
    return f"""You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within {word_count} words. Please provide the summary of the text given here: """

def extract_video_id(url):
    if "youtu.be" in url:
        return url.split("/")[-1]
    elif "youtube.com" in url:
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "embed/" in url:
            return url.split("embed/")[1].split("?")[0]
    return None

def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(entry["text"] for entry in transcript)
    except Exception as e:
        st.warning(f"Error fetching transcript: {str(e)}")
        return None

def generate_gemini_content(transcript_text, prompt):
    try:
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

st.title("YouTube Video Summarizer")

# Add option to choose summary word count
word_count = st.slider("Choose the number of words in the summary", min_value=50, max_value=2500, value=250, step=50)

# Create tabs for URL input and file upload
tab1, tab2 = st.tabs(["Enter YouTube URL", "Upload Video File"])

with tab1:
    youtube_link = st.text_input("Enter YouTube Video Link:")

    if st.button("Generate Summary from URL"):
        if youtube_link:
            video_id = extract_video_id(youtube_link)
            if video_id:
                transcript_text = fetch_transcript(video_id)
                if transcript_text:
                    prompt = generate_prompt(word_count)
                    summary = generate_gemini_content(transcript_text, prompt)
                    if summary:
                        st.write("## Detailed Notes:")
                        st.write(summary)
                        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", caption="Video Thumbnail")
                else:
                    st.warning("Could not automatically retrieve transcript.")
                    manual_transcript = st.text_area("Please paste the video transcript here:")
                    if manual_transcript and st.button("Summarize Manual Transcript"):
                        prompt = generate_prompt(word_count)
                        summary = generate_gemini_content(manual_transcript, prompt)
                        if summary:
                            st.write("## Detailed Notes (from manual transcript):")
                            st.write(summary)
            else:
                st.error("Invalid YouTube URL. Please check the link and try again.")
        else:
            st.warning("Please enter a YouTube video link.")

with tab2:
    uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "avi", "mov"])
    if uploaded_file is not None:
        st.video(uploaded_file)
        st.warning("Note: This app cannot automatically transcribe uploaded videos. Please provide the transcript manually.")
        manual_transcript = st.text_area("Please paste the video transcript here:")
        if manual_transcript and st.button("Summarize Uploaded Video Transcript"):
            prompt = generate_prompt(word_count)
            summary = generate_gemini_content(manual_transcript, prompt)
            if summary:
                st.write("## Detailed Notes (from uploaded video transcript):")
                st.write(summary)

st.markdown("---")
st.write("Note: If automatic transcript retrieval fails, you can manually paste the transcript above.")
