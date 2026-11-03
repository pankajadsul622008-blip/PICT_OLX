import os
import sys
import json
import base64
import mimetypes
from pathlib import Path
from sarvamai import SarvamAI

# Ensure environment variables are loaded
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")

def get_sarvam_client() -> SarvamAI:
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        raise ValueError("SARVAM_API_KEY is not set. Please add it to your .env file.")
    return SarvamAI(api_subscription_key=api_key)

def encode_image_to_data_uri(image_path: str) -> str:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found at: {image_path}")
    
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type or not mime_type.startswith("image/"):
        mime_type = "image/jpeg"
        
    with open(path, "rb") as img_file:
        b64_data = base64.b64encode(img_file.read()).decode("utf-8")
        
    return f"data:{mime_type};base64,{b64_data}"

def generate_listing_from_image(image_path: str, model: str = "gemma4") -> dict:
    """
    Analyzes an uploaded picture of study material (book, notes, drafter, etc.)
    and returns a structured listing tailored for PICT / SPPU engineering students.
    """
    client = get_sarvam_client()
    data_uri = encode_image_to_data_uri(image_path)
    
    system_prompt = (
        "You are an AI assistant for a college study material marketplace at PICT "
        "(Pune Institute of Computer Technology, affiliated with SPPU - Pune University). "
        "A student is listing their used study material (textbook, handwritten notes, PYQ booklet, "
        "lab manual, engineering drafter/kit, etc.).\n"
        "Analyze the provided image and extract accurate details.\n"
        "Return ONLY a valid JSON object with the following keys:\n"
        "{\n"
        '  "title": "Clean, descriptive title for the listing",\n'
        '  "subject": "Subject name according to SPPU curriculum (e.g. Data Structures, OS, CN, TOC, EM-3)",\n'
        '  "department": "One of: Computer Engineering, Information Technology, E&TC, AIDS, First Year (FE), or General",\n'
        '  "target_year": "One of: FE, SE, TE, BE",\n'
        '  "semester": "Semester 1 through 8",\n'
        '  "material_type": "One of: Textbook, Handwritten Notes, Question Bank / PYQ, Lab Manual, Tool / Instrument",\n'
        '  "publisher_or_author": "e.g. Nirali Prakashan, TechKnowledge, Pearson, McGraw-Hill, or Senior Handwritten",\n'
        '  "detected_condition": "One of: Like New, Good, Annotated / Highlighted, Fair / Worn",\n'
        '  "suggested_price_inr": integer resale price in INR (reasonable campus second-hand price, usually 40-60% off MRP),\n'
        '  "estimated_mrp_inr": integer estimated original MRP in INR,\n'
        '  "description": "A helpful 2-sentence description for juniors highlighting utility and condition",\n'
        '  "search_tags": ["list", "of", "relevant", "search", "keywords"]\n'
        "}\n"
        "Do not include any markdown backticks or commentary outside the JSON."
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
    
    # Strip markdown code fencing if returned
    if content.startswith("```"):
        lines = content.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines).strip()
        
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback raw payload if LLM didn't return strict JSON
        return {
            "raw_text": content,
            "error": "Failed to parse structured JSON from model response"
        }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        img_file = sys.argv[1]
    else:
        print("Usage: python auto_lister.py <path_to_image>")
        print("Example: python auto_lister.py sample_book.jpg")
        sys.exit(0)
        
    print(f"Analyzing {img_file} with Sarvam AI Vision...")
    result = generate_listing_from_image(img_file)
    print("\n--- Generated Marketplace Listing ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))
