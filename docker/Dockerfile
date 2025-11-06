# ---- Base image ----
FROM python:3.12-slim

# Prevent Python from buffering logs & writing .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory inside the container
WORKDIR /app

# Copy only requirements first (for caching)
COPY ../requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY ../ .

# Expose Flask port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
