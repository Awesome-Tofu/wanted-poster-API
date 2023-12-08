# main.py

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from io import BytesIO
import os
import requests
from app.wantedposter.wantedposter import WantedPoster

app = FastAPI()

def download_image(url: str):
    response = requests.get(url)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        raise HTTPException(status_code=400, detail="Failed to download image from URL")

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
            image_data = download_image(image_source)
        else:
            # If the image source is already image data (local file path or BytesIO), use it directly
            image_data = image_source

        # Create WantedPoster object
        wanted_poster = WantedPoster(image_data, first_name, last_name, bounty_amount)

        # Generate poster
        poster_path = wanted_poster.generate(should_make_portrait_transparent=True)

        if isinstance(poster_path, str):
            # If the poster path is a string, it means it's a file path
            with open(poster_path, 'rb') as poster_file:
                poster_data = poster_file.read()
        else:
            # If the poster path is a BytesIO object, get the bytes
            poster_data = poster_path.getvalue()

        # Delete the generated image
        if isinstance(poster_path, BytesIO):
            poster_path.close()

        # Return the image data as a response
        return StreamingResponse(BytesIO(poster_data), media_type="image/jpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
