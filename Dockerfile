# Use an official Python runtime as a parent image.
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the code
COPY . /app/

# Expose port 8080 for OpenShift
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]
