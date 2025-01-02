# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy application code and requirements
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the Flask app will run on
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "app.py"]
