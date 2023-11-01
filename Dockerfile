# Use the official Python image as the base image
FROM python:3.7-alpine

# Set the working directory
WORKDIR /code

# Set environment variables for Flask
ENV FLASK_APP=test_api.py
ENV FLASK_RUN_HOST=0.0.0.0

# Install dependencies
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt 
RUN pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 4000

# Copy the current directory contents into the container at /code
COPY . .

# Command to run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=4000"]
