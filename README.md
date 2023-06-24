*OpenCopilot, an AI-driven Copilot Agent is designed to offer an efficient and controllable framework for software companies. OpenCopilot seamlessly integrates with a company's software ecosystem and performs complex tasks with minimal guidance.*


## Getting started
> Do not forget to include your OpenAI keys in the *env.py* after making your own copy from *service/env.py.example*

### **1. On your local machine**
**a. Backend**
###### Install requirements:
* `cd service && pip3 install -r requirements.txt`

###### Run the server:
* `cd service && python3 -m uvicorn main:app --reload`

**b. Frontend**

###### Run web chatbot:
* `cd chat-fe`
* `npm install --legacy-peer-deps`
* `npm start`

**c. Database**
###### Build meta database:
* `cd service && python3 initialize_chromaDB.py`




### **2. On Docker**
> Before you begin, make sure you have Docker and Docker Compose installed on your machine.

1. Open a terminal or command prompt window and navigate to the project directory.
2. Run the following command to start the application:
	 `docker-compose up`
3. Once the application is running, you can access it in your web browser at http://localhost:3000/
