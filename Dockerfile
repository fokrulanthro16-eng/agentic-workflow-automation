# Use the official Python lightweight image
FROM python:3.11-slim

# Set environment configurations
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Set target directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source files
COPY src/ src/
COPY docs/ docs/

# Expose the service port
EXPOSE 8080

# Start FastAPI server
CMD ["python", "src/main.py", "--server"]
