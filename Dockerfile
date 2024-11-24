# Use the official Python devcontainer image as the base image
FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /workspaces/engine-main

# Copy the application files into the container
COPY . /workspaces/engine-main/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your Flask app runs on
EXPOSE 5000
