import os
from typing import Optional
from ..config import (
    CLOUDINARY_URL,
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
)

IS_CLOUDINARY_AVAILABLE = False

try:
    import cloudinary
    import cloudinary.uploader

    if CLOUDINARY_URL:
        cloudinary.config(cloudinary_url=CLOUDINARY_URL)
        IS_CLOUDINARY_AVAILABLE = True
    elif CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True,
        )
        IS_CLOUDINARY_AVAILABLE = True
except ImportError:
    pass

def is_configured() -> bool:
    return IS_CLOUDINARY_AVAILABLE

def upload_image(image_input: str, folder: str = "pict_marketplace") -> str:
    """
    Uploads an image (base64 data URI, file path, or URL) to Cloudinary CDN.
    Automatically applies auto-quality and auto-format (WebP) compression.
    Returns the secure CDN URL (or original image_input if Cloudinary upload fails).
    """
    if not is_configured() or not image_input:
        return image_input

    # If it is already a Cloudinary or remote URL, no need to re-upload
    if image_input.startswith("http://") or image_input.startswith("https://"):
        return image_input

    try:
        response = cloudinary.uploader.upload(
            image_input,
            folder=folder,
            resource_type="image",
            transformation=[
                {"quality": "auto", "fetch_format": "auto"},
                {"width": 1000, "crop": "limit"}
            ],
        )
        secure_url = response.get("secure_url")
        if secure_url:
            print(f"Cloudinary upload success: {secure_url}")
            return secure_url
    except Exception as e:
        print(f"Cloudinary upload warning: {e}. Falling back to original image.")

    return image_input
