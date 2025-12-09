import os
import requests

from urllib.parse import urlparse

from django.core.files.base import ContentFile


def save_profile_picture_from_url(user, picture_url):
    if not picture_url:
        return

    try:
        response = requests.get(picture_url, timeout=10)
        if response.status_code == 200:
            # Extract filename from URL
            path = urlparse(picture_url).path
            filename = os.path.basename(path) or f"{user.username}.jpg"
            if not filename.endswith(".jpg"):
                filename = filename + ".jpg"

            # Save file to ImageField
            user.image.save(
                filename, ContentFile(response.content), save=True
            )
    except Exception as e:
        print(f"Error saving profile picture: {e}")
