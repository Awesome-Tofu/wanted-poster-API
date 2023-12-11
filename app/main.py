from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from io import BytesIO
import os
import requests
from PIL import Image
from app.wantedposter.wantedposter import WantedPoster

app = FastAPI()

TMP_IMAGES_DIR = "/tmp/images"  # Define the directory to store images

def download_image(url: str, save_path: str):
    try:
        response = requests.get(url, verify=True)  # Verify SSL certificates
        response.raise_for_status()  # Raise HTTPError for bad responses
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as file:
            file.write(response.content)
        return True
    except requests.RequestException as e:
        # Log the error for debugging purposes
        print(f"Failed to download image from URL: {str(e)}")
        return False

@app.get("/generate-poster")
async def generate_poster(
    image_source: str = Query(..., title="Image Source", description="URL or local file path"),
    first_name: str = Query(..., title="First Name"),
    last_name: str = Query(..., title="Last Name"),
    bounty_amount: int = Query(0, title="Bounty Amount")
):
    try:
        # Validate input parameters
        if not isinstance(bounty_amount, int) or bounty_amount < 0:
            raise HTTPException(status_code=400, detail="Invalid bounty amount")

        if image_source.startswith("http"):
            # If the image source is a URL, download the image to /tmp/images
            image_path = os.path.join(TMP_IMAGES_DIR, f"downloaded_image_{first_name}_{last_name}.png")
            if not download_image(image_source, image_path):
                raise HTTPException(status_code=400, detail="Failed to download image from URL")
        else:
            # If the image source is a local file path
            image_path = image_source

        # Create WantedPoster object
        wanted_poster = WantedPoster(image_path, first_name, last_name, bounty_amount)

        # Generate poster
        poster_path = wanted_poster.generate(should_make_portrait_transparent=True)

        # Save the poster with a unique name in /tmp/images
        save_path = os.path.join(TMP_IMAGES_DIR, f"poster_{first_name}_{last_name}.jpg")
        Image.open(poster_path).save(save_path)

        return StreamingResponse(open(save_path, 'rb'), media_type="image/jpeg")

    except Exception as e:
        # Log the error for debugging purposes
        print(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        # Cleanup: Delete the generated image
        if os.path.exists(poster_path):
            os.remove(poster_path)
