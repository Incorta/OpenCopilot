# backend/Dockerfile

# Use the official Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY ./service/* ./

# Install the Python dependencies
RUN pip3 install -r requirements.txt

# Set the PYTHONPATH (Important to allow relative path imports)
#CMD ["sh", "-c", "PYTHONPATH=$(pwd) uvicorn main:app --host 0.0.0.0 --port 8000"]

CMD ["/bin/bash", "-c", "exec /bin/bash"]

