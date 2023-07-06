# backend/Dockerfile

# Use the official Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the directories
COPY ./service ./service
COPY ./opencopilot ./opencopilot
COPY ./start.sh ./

# Install the Python dependencies
RUN pip3 install -r ./service/requirements.txt

# Run the server (Set the PYTHONPATH (Important to allow relative path imports))
CMD ["sh", "-c", "./start.sh"]

