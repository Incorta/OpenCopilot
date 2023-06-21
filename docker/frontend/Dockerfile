# frontend/Dockerfile

# Use the official Node.js image
FROM node:16

# Set the working directory
WORKDIR /app

# Copy the package.json file
COPY ./chat-fe/package.json .

# Install the Node.js dependencies
RUN npm install --legacy-peer-deps

# Copy the rest of the code
COPY ./chat-fe .

# Set the command to start the app
CMD ["npm", "start"]
