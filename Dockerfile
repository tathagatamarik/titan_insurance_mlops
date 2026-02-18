# 1. Base Image
FROM python:3.9-slim

# 2. Set Working Directory
WORKDIR /app

# 3. Install Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy Code (Scripts and Source)
COPY scripts/ ./scripts
COPY src/ ./src

# --- THE FIX ---
# 5. Create the data directory manually (since Git didn't send it)
RUN mkdir -p data

# 6. Generate Data inside the image
RUN python scripts/generate_data.py
# ---------------

# 7. Train the model (It will find the data generated above)
RUN python src/train.py

# 8. Expose Port
EXPOSE 5000

# 9. Start API
CMD ["python", "src/app.py"]