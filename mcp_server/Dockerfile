# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the server code
COPY . .

# Expose the main and generated API ports
EXPOSE 8000
EXPOSE 8001

# Start the server using the new startup script
CMD ["python", "start_mcp_server.py"]