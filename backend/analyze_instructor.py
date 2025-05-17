import requests
import webvtt
import os
from textblob import TextBlob

# ✅ Load unprofessional words from an external source
def load_unprofessional_words_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return [line.strip().lower() for line in response.text.splitlines() if line.strip()]
    except Exception as e:
        print(f"Error loading unprofessional words: {e}")
    return []

#def load_unprofessional_words(filepath="unprofessional_words.txt"):
#    with open(filepath, "r", encoding="utf-8") as f:
#        return [line.strip().lower() for line in f if line.strip()]

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

    # NLP Analysis
    signals = []
    red_flags = []

    # ✅ Load global unprofessional keyword list
    keyword_url = "https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/master/en"
    unprofessional_keywords = load_unprofessional_words_from_url(keyword_url)
    # unprofessional_keywords = load_unprofessional_words()
    # unprofessional_found = [word for word in unprofessional_keywords if word in plain_text.lower()]

    behavior_score = 5  # Start with highest

    # 1. Tone and Sentiment
    blob = TextBlob(plain_text)
    polarity = blob.sentiment.polarity
    if polarity < -0.5:
        behavior_score = 1
    elif polarity < -0.2:
        behavior_score = 2
    elif polarity < 0:
        behavior_score = 3
    elif polarity < 0.3:
        behavior_score = 4

    # 2. Red Flags
    if "I don't care" in plain_text or "whatever" in plain_text:
        red_flags.append("Dismissive language")
    if "you’re wrong" in plain_text.lower():
        red_flags.append("Blaming student")
    if polarity < -0.2:
        red_flags.append("Negative emotional tone")

    # 3. Unprofessional Words
    found_unprofessional = []
    for word in unprofessional_keywords:
        if word in plain_text.lower():
            found_unprofessional.append(word)
            red_flags.append(f"Unprofessional phrase: '{word}'")

    # 4. Reduced participation
    if len(plain_text.split()) < 100:
        signals.append({"signal": "Reduced speech/chat participation", "risk": "Medium"})

    # 5. Simulated risk signals
    signals.append({"signal": "Missed 3+ sessions in a row", "risk": "High"})
    signals.append({"signal": "Not logging into the app", "risk": "Medium"})

    if "I used to love" in plain_text or "not doing that anymore" in plain_text:
        signals.append({"signal": "Skipping favorite activities", "risk": "Medium to High"})

    if any(x in plain_text.lower() for x in ["i'm tired", "i can't", "why bother", "alone"]):
        signals.append({"signal": "Sad/withdrawn text patterns", "risk": "High"})

    return {
        "video_id": video_id,
        "behavior_score": f"{behavior_score}/5",
        "red_flags": red_flags,
        "overall_rating": f"{behavior_score}/5",
        "unprofessional_phrases": found_unprofessional,
        "risk_signals": signals
    }
