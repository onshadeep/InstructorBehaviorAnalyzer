import requests
import webvtt
import os
from openai import OpenAI

def analyze_video(video_id):
    VIMEO_ACCESS_TOKEN = os.getenv("VIMEO_ACCESS_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    headers = {
        "Authorization": f"Bearer {VIMEO_ACCESS_TOKEN}"
    }

    track_res = requests.get(f"https://api.vimeo.com/videos/{video_id}/texttracks", headers=headers)
    track_data = track_res.json()

    vtt_url = None
    for track in track_data.get('data', []):
        if track['language'] == 'en':
            vtt_url = track['link']
            break

    if not vtt_url and track_data.get('data'):
        vtt_url = track_data['data'][0]['link']

    if not vtt_url:
        raise Exception("No transcript available")

    vtt_response = requests.get(vtt_url)
    os.makedirs("transcripts", exist_ok=True)
    vtt_path = f"transcripts/{video_id}.vtt"
    with open(vtt_path, "wb") as f:
        f.write(vtt_response.content)

    plain_text = ""
    for caption in webvtt.read(vtt_path):
        plain_text += caption.text + "\n"

    transcript_path = f"transcripts/{video_id}.txt"
    with open(transcript_path, "w") as f:
        f.write(plain_text)

    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""
    Analyze the following class transcript.

    Rate the instructor's tone and behavior on a scale of 1 (very rude) to 5 (very professional).
    List any red flags in behavior or language.

    Transcript:
    {plain_text}
    """

#    response = client.chat.completions.create(
#       model="gpt-3.5-turbo",
#        messages=[
#            {"role": "system", "content": "You are a class behavior reviewer."},
#            {"role": "user", "content": prompt}
#        ]
#    )

#    analysis = response.choices[0].message.content

# Instead of calling OpenAI
     analysis = "Instructor rating: 5\nNo red flags detected.\n(Virtual output for testing)"

    os.makedirs("analysis", exist_ok=True)
    analysis_path = f"analysis/{video_id}.txt"
    with open(analysis_path, "w") as f:
        f.write(analysis)

    return analysis
