# Base image
FROM python:3.12.8-slim-bullseye

# Set working directory
WORKDIR /runtime

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app
COPY context.py .
COPY runtime.py .

# Set the default command to run the Flask app
CMD ["python", "runtime.py"]