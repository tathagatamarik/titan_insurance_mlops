# 1. Base Image (The OS)
FROM python:3.9-slim

# 2. Work Directory
WORKDIR /app

# 3. Install Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy Code
COPY src/ ./src
COPY data/ ./data

# 5. Train Model during build (So the image comes with a trained brain)
RUN python src/train.py

# 6. Command to run when container starts (We will change this later for API)
CMD ["python", "src/train.py"]