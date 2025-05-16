import requests
import webvtt
import os
from openai import OpenAI

def analyze_video(video_id):
    # Fetch environment variables
    VIMEO_ACCESS_TOKEN = os.getenv("VIMEO_ACCESS_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Define headers for Vimeo API request
    headers = {
        "Authorization": f"Bearer {VIMEO_ACCESS_TOKEN}"
    }

    # Fetch text tracks from Vimeo API
    track_res = requests.get(f"https://api.vimeo.com/videos/{video_id}/texttracks", headers=headers)
    track_data = track_res.json()

    # Look for English subtitle track
    vtt_url = None
    for track in track_data.get('data', []):
        if track['language'] == 'en':
            vtt_url = track['link']
            break

    # If no English subtitle found, use the first available track
    if not vtt_url and track_data.get('data'):
        vtt_url = track_data['data'][0]['link']

    # If no track URL found, raise an exception
    if not vtt_url:
        raise Exception("No transcript available")

    # Fetch the VTT file from Vimeo
    vtt_response = requests.get(vtt_url)
    os.makedirs("transcripts", exist_ok=True)
    vtt_path = f"transcripts/{video_id}.vtt"
    with open(vtt_path, "wb") as f:
        f.write(vtt_response.content)

    # Convert the VTT file to plain text
    plain_text = ""
    for caption in webvtt.read(vtt_path):
        plain_text += caption.text + "\n"

    # Save the plain text as a .txt file
    transcript_path = f"transcripts/{video_id}.txt"
    with open(transcript_path, "w") as f:
        f.write(plain_text)

    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Prepare the prompt for analyzing the instructor's behavior
    prompt = f"""
    Analyze the following class transcript.

    Rate the instructor's tone and behavior on a scale of 1 (very rude) to 5 (very professional).
    List any red flags in behavior or language.

    Transcript:
    {plain_text}
    """

    # For testing purposes, we are mocking the OpenAI response
    # Uncomment the below code when ready to use OpenAI API
    # response = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": "You are a class behavior reviewer."},
    #         {"role": "user", "content": prompt}
    #     ]
    # )
    # analysis = response.choices[0].message.content

    # Instead of calling OpenAI, use mock data for testing
    analysis = "Instructor rating: 5\nNo red flags detected.\n(Virtual output for testing)"

    # Save the analysis to a file
    os.makedirs("analysis", exist_ok=True)
    analysis_path = f"analysis/{video_id}.txt"
    with open(analysis_path, "w") as f:
        f.write(analysis)

    return analysis
