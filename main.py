from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image
import io

app = FastAPI()

@app.post("/upload")
async def upload_image(max_size:int, file: UploadFile = File(...)):
    image = Image.open(file.file)

    # Resize the image if it exceeds max size
    if image.width > max_size or image.height > max_size:
        ratio = min(max_size / image.width, max_size / image.height)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        image = image.resize(new_size, Image.LANCZOS)

    # Save image to a BytesIO object
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG') # or other format as needed
    img_byte_arr.seek(0)

    return StreamingResponse(img_byte_arr, media_type="image/png")

