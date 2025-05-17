import requests
import webvtt
import os
from textblob import TextBlob

# ✅ Load list of phrases from a URL (used for unprofessional words and red flags)
def load_phrases_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return [line.strip().lower() for line in response.text.splitlines() if line.strip()]
    except Exception as e:
        print(f"Error loading phrases from URL: {e}")
    return []

def analyze_video(video_id):
    VIMEO_ACCESS_TOKEN = os.getenv("VIMEO_ACCESS_TOKEN")

    headers = {
        "Authorization": f"Bearer {VIMEO_ACCESS_TOKEN}"
    }

    # Get transcript link
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

    # Download and save VTT
    vtt_response = requests.get(vtt_url)
    os.makedirs("transcripts", exist_ok=True)
    vtt_path = f"transcripts/{video_id}.vtt"
    with open(vtt_path, "wb") as f:
        f.write(vtt_response.content)

    # Extract plain text
    plain_text = ""
    for caption in webvtt.read(vtt_path):
        plain_text += caption.text + "\n"

    # Save transcript
    transcript_path = f"transcripts/{video_id}.txt"
    with open(transcript_path, "w") as f:
        f.write(plain_text)

    plain_text_lower = plain_text.lower()
    red_flags = []
    signals = []

    # ✅ Load external word lists
    unprofessional_url = "https://raw.githubusercontent.com/onshadeep/unprofessional_words/refs/heads/main/unprofessional_words.txt"
    red_flag_url = "https://raw.githubusercontent.com/onshadeep/unprofessional_words/refs/heads/main/red_flags.txt"

    unprofessional_keywords = load_phrases_from_url(unprofessional_url)
    red_flag_phrases = load_phrases_from_url(red_flag_url)

    # ✅ Analyze sentiment (tone)
    blob = TextBlob(plain_text)
    polarity = blob.sentiment.polarity

    behavior_score = 5
    tone_score = 5

    # Behavior score based on sentiment
    if polarity < -0.5:
        behavior_score = 1
    elif polarity < -0.2:
        behavior_score = 2
    elif polarity < 0:
        behavior_score = 3
    elif polarity < 0.3:
        behavior_score = 4

    # Tone score based on overall emotional tone
    if polarity < -0.4:
        tone_score = 2
    elif polarity < -0.2:
        tone_score = 3
    elif polarity < 0:
        tone_score = 4

    # ✅ Red Flags from list
    for phrase in red_flag_phrases:
        if phrase in plain_text_lower:
            red_flags.append(f"Red Flag phrase: '{phrase}'")

    # ✅ Unprofessional Words
    found_unprofessional = []
    for word in unprofessional_keywords:
        if word in plain_text_lower:
            found_unprofessional.append(word)
            red_flags.append(f"Unprofessional phrase: '{word}'")

    # ✅ Risk signals
    if len(plain_text.split()) < 100:
        signals.append({"signal": "Reduced speech/chat participation", "risk": "Medium"})

    signals.append({"signal": "Missed 3+ sessions in a row", "risk": "High"})
    signals.append({"signal": "Not logging into the app", "risk": "Medium"})

    if any(phrase in plain_text_lower for phrase in ["i used to love", "not doing that anymore"]):
        signals.append({"signal": "Skipping favorite activities", "risk": "Medium to High"})

    if any(phrase in plain_text_lower for phrase in ["i'm tired", "i can't", "why bother", "alone"]):
        signals.append({"signal": "Sad/withdrawn text patterns", "risk": "High"})

    # ✅ Final output
    overall_score = round((behavior_score + tone_score) / 2, 2)

    return {
        "video_id": video_id,
        "behavior_score": f"{behavior_score}/5",
        "tone_score": f"{tone_score}/5",
        "overall_rating": f"{overall_score}/5",
        "red_flags": red_flags,
        "unprofessional_phrases": found_unprofessional,
        "risk_signals": signals
    }
