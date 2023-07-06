# backend/Dockerfile

# Use the official Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY ./service/requirements.txt ./

# Install the Python dependencies
RUN pip3 install -r requirements.txt

# Copy the directories
COPY ./service ./service
COPY ./sdk ./sdk

ENV PYTHONPATH=/app:/app/service:/app/sdk

# Run the server (Set the PYTHONPATH (Important to allow relative path imports))
CMD ["sh", "-c", "ls && cd service && uvicorn main:app --host 0.0.0.0 --port 8000"]

