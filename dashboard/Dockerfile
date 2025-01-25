# Base image
FROM python:3.12.8-slim-bullseye

# Set working directory
WORKDIR /dashboard

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app
COPY dashboard.py .

# Expose port 8050
EXPOSE 8050

# Set the default command to run the Flask app
CMD ["python", "app.py"]