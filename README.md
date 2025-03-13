# **ThreadedTalk**  

**ThreadedTalk** is a FastAPI-based application that serves as a client interface for a deployed **LangGraph agent**. It enables structured conversation handling, real-time streaming responses, and optimized cleanup of inactive conversations using **LangGraph SDK**.  

## **Features**  

✅ **LangGraph Integration** – Interacts with a deployed LangGraph agent for conversation management.  
✅ **Threaded Conversations** – Each conversation is mapped to a unique thread ID stored in a database.  
✅ **Message Streaming** – Supports both synchronous and streaming-based responses.  
✅ **Conversation Management** – Create, retrieve, and delete conversations dynamically.  
✅ **Optimized Cleanup** – Deletes inactive conversations based on a given timestamp.  
✅ **Database Support** – Uses PostgreSQL/MySQL for persistent storage.  

## **API Endpoints**  

### **1. Conversation API**  
- `POST /conversation` – Create a conversation and get a thread ID.  
- `POST /conversation/message` – Send a message to the LangGraph agent.  
- `POST /conversation/stream` – Stream conversation responses from the LangGraph agent.  

### **2. Delete API**  
- `DELETE /conversation/{conversation_id}` – Deletes a conversation and its associated thread.  

### **3. Cleanup API**  
- `DELETE /conversation/cleanup?unused_since=<timestamp>` – Deletes inactive conversations before the specified timestamp.  

## **Installation**  

### **Prerequisites**  
- **Python 3.11+**  
- **PostgreSQL/MySQL** (configured as per database settings)  
- **LangGraph SDK** (installed via `requirements.txt`)  

### **Setup & Install Dependencies**  
```sh
pip install -r requirements.txt
```

## **Running the Project**  
```sh
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```