import os
from pathlib import Path
from sarvamai import SarvamAI

# Load .env file into environment if present
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip().strip("'\"")

def get_sarvam_client():
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        raise ValueError("SARVAM_API_KEY is not set. Please add your key to the .env file.")
    return SarvamAI(api_subscription_key=api_key)

if __name__ == "__main__":
    client = get_sarvam_client()
    response = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=[
            {"role": "user", "content": "Hello! Please give a one-sentence greeting."}
        ],
    )
    print(response.choices[0].message.content)
