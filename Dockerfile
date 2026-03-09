FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for sentence-transformers
RUN apt-get update && apt-get install -y git gcc g++ && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip

# Install CPU-only torch
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install everything normally
RUN pip install requests beautifulsoup4 sentence-transformers numpy aiohttp urllib3

RUN pip3 install urllib3

COPY . /app

# Start scanning script
CMD ["python", "main.py"]
