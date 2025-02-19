# 使用官方 Python 映像作為基礎映像
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 安裝所需的依賴
RUN pip install --no-cache-dir -r requirements.txt

# 設定容器啟動時執行的命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]