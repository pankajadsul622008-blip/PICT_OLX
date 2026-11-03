import os
import json
from sarvamai import SarvamAI
from ..config import SARVAM_API_KEY

def get_sarvam_client() -> SarvamAI:
    key = os.environ.get("SARVAM_API_KEY") or SARVAM_API_KEY
    if not key:
        raise ValueError("SARVAM_API_KEY is not set. Please add it to your .env file or environment.")
    return SarvamAI(api_subscription_key=key)

def analyze_study_material_image(data_uri: str, model: str = "gemma4") -> dict:
    """
    Sends study material image to Sarvam AI Vision and extracts SPPU/PICT metadata.
    """
    client = get_sarvam_client()
    system_prompt = (
        "You are an AI assistant for a college study material marketplace at PICT "
        "(Pune Institute of Computer Technology, affiliated with SPPU - Pune University). "
        "A senior student is listing used study material (textbook, handwritten notes, "
        "PYQ question booklet, lab manual, engineering drafter/kit).\n"
        "Analyze the provided image and extract accurate details.\n"
        "Return ONLY a valid JSON object with the following keys:\n"
        "{\n"
        '  "title": "Clean, descriptive title for the listing",\n'
        '  "subject": "Subject name according to SPPU curriculum (e.g. Data Structures, OS, CN, TOC, EM-3)",\n'
        '  "department": "One of: Computer Engineering, Information Technology, E&TC, AIDS, First Year (FE), General",\n'
        '  "target_year": "One of: FE, SE, TE, BE",\n'
        '  "semester": "Semester 1 through 8",\n'
        '  "material_type": "One of: Textbook, Handwritten Notes, Question Bank / PYQ, Lab Manual, Tool / Instrument",\n'
        '  "publisher_or_author": "e.g. Nirali Prakashan, TechKnowledge, Pearson, McGraw-Hill, or Senior Handwritten",\n'
        '  "detected_condition": "One of: Like New, Good, Annotated / Highlighted, Fair / Worn",\n'
        '  "suggested_price_inr": integer resale price in INR (40-60% off typical MRP),\n'
        '  "estimated_mrp_inr": integer estimated original MRP in INR,\n'
        '  "description": "A helpful 2-sentence description for juniors highlighting utility and condition",\n'
        '  "search_tags": ["list", "of", "relevant", "keywords"]\n'
        "}\n"
        "Do not include any markdown backticks or extra text outside JSON."
    )
    
    response = client.chat.completions_v2(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": system_prompt},
                    {"type": "image_url", "image_url": {"url": data_uri}}
                ]
            }
        ],
        temperature=0.2
    )
    
    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        lines = content.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines).strip()
    return json.loads(content)

def test_connection():
    """Verifies connection to Sarvam AI API."""
    client = get_sarvam_client()
    print("Testing connection with sarvam-105b-conversations...")
    res = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print("Response:", res.choices[0].message.content)
