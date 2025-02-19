from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image
import io
import requests
import json
from pydantic import BaseModel


class CallRequest(BaseModel):
    query: str
    agent_token: str
    userid: str
    agent_host: str

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

@app.post("/agent-proxy")
async def agent_proxy(callRequest:CallRequest):
    json_body = {
        "inputs": {},
        "query": callRequest.query,
        "response_mode": "streaming",
        "conversation_id": "",
        "user": callRequest.userid,
        "files": []
    }

    headers = {
        "Authorization": f"Bearer {callRequest.agent_token}",
        "Content-Type":  "application/json"
    }

    response = requests.post(callRequest.agent_host, json=json_body, headers=headers)
    arg1 = response.text
    arg1 = arg1.replace("event: ping\n\n", "")
    arg1 = arg1.replace("data: ", ",")
    arg1 = arg1.replace(",", "", 1)  # 只替換第一次出現的逗號
    arg1 = '[' + arg1 + ']'
    
    events = json.loads(arg1)
    last29_items = events[-3:]  # 取最後29個項目
    return last29_items
