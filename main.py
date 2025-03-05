from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image
import io
import requests
import json
from pydantic import BaseModel
import os

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
    for item in last29_items:
        item.pop("metadata", None)  # 移除 metadata 屬性（如果存在）
    return last29_items

@app.get("/search",summary="search engine",
    description="categories available options: general, images,news,vidoes, map, files")
async def search(q: str, categories: str = "general"):
    page_size = int(os.environ.get("PAGE_SIZE", "10"))
    searxng_endpoint = os.environ.get("SEARXNG_ENDPOINT", "http://192.168.1.15:8277")
    search_result_format = os.environ.get("SEARCH_RESULT_FORMAT", "json")

    url = f"{searxng_endpoint}?q={q}&format={search_result_format}&categories={categories}"
    print(url)
    response = requests.get(url)
    results = response.json()

    return results["results"][:page_size]
