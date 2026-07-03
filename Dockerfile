FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir ".[server,cli]"
EXPOSE 8000
ENV QUORUM_MAX_COUNCILORS=7
CMD ["uvicorn", "quorum.server:app", "--host", "0.0.0.0", "--port", "8000"]
