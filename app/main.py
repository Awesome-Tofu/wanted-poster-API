from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
import os
import requests
from PIL import Image
from app.wantedposter.wantedposter import WantedPoster

app = FastAPI()

def download_image(url: str, save_path: str):
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as file:
            file.write(response.content)
        return True
    else:
        return False

@app.get("/generate-poster")
async def generate_poster(
    image_source: str = Query(..., title="Image Source", description="URL or local file path"),
    first_name: str = Query(..., title="First Name"),
    last_name: str = Query(..., title="Last Name"),
    bounty_amount: int = Query(0, title="Bounty Amount")
):
    try:
        if image_source.startswith("http"):
            # If the image source is a URL, download the image
            image_path = os.path.join("images", "downloaded_image.png")
            if not download_image(image_source, image_path):
                raise HTTPException(status_code=400, detail="Failed to download image from URL")
        else:
            # If the image source is a local file path
            image_path = image_source

        # Create WantedPoster object
        wanted_poster = WantedPoster(image_path, first_name, last_name, bounty_amount)

        # Generate poster
        poster_path = wanted_poster.generate(should_make_portrait_transparent=True)

        # Save the poster with the desired name in the "images" folder
        save_path = os.path.join("images", "poster.jpg")
        Image.open(poster_path).save(save_path)

        # Delete the generated image
        os.remove(poster_path)

        return FileResponse(save_path, media_type="image/jpeg", filename="poster.jpg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
