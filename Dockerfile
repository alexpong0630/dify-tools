# 使用官方 Python 映像作為基礎映像
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 複製當前目錄的內容到容器的 /app 目錄
COPY . .

# 安裝所需的依賴（如果有 requirements.txt，則可以取消註解）
# RUN pip install --no-cache-dir -r requirements.txt

# 安裝所需的依賴
RUN pip install --no-cache-dir -r requirements.txt

# 設定容器啟動時執行的命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]