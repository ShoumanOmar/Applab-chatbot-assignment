# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Create directory for uploaded files
RUN mkdir -p uploaded_files

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8000

# Run the application when the container launches
CMD ["python", "backend.py"]