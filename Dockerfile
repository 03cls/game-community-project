# Hugging Face Spaces — Docker SDK 部署
# 规范：服务必须监听 7860 端口，绑定 0.0.0.0
FROM python:3.11-slim

WORKDIR /app

# 先装依赖（利用 Docker 层缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝项目代码
COPY . .

# 云端无本地 Ollama：AI 对话/审核自动走内置规则引擎，零外部依赖
ENV OLLAMA_ENABLED=0 \
    SQLALCHEMY_SILENCE_UBER_WARNING=1 \
    PYTHONUNBUFFERED=1

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
