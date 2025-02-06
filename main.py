from fastapi import FastAPI, UploadFile, File
from typing import Annotated
import answering_engine as ae
from pymongo import MongoClient
import json
import uuid
from typing import Optional
from pymongo.server_api import ServerApi
from llama_index.core.agent import AgentRunner
from llama_index.llms.openai import OpenAI
from llama_index.core.chat_engine import SimpleChatEngine
from langchain_community.document_loaders import TextLoader
import fitz
import PyPDF2
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import PyPDFLoader
from langchain.docstore.document import Document

app = FastAPI()

def _init():
    # Replace with your MongoDB connection string
    MONGO_URI = "mongodb+srv://sunnymurali:rZPTs1dslFCUbxbh@cluster0.46yro.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    # Change this to your actual URI

    # Create a connection to MongoDB
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

@app.get("/")
async def root():
    return {"message": "Hello World"}


from fastapi import FastAPI
from pydantic import BaseModel


class Question(BaseModel):
    query: str

class Agent(BaseModel):
    agent_id: Optional[str]  
    agent_name: str
    prompt: str
    llm_model: str

@app.post("/createAgent/")
async def create_agent(agent: Agent):
    try:
        MONGO_URI = "mongodb+srv://sunnymurali:rZPTs1dslFCUbxbh@cluster0.46yro.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        # Change this to your actual URI

        # Create a connection to MongoDB
        client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        db = client["agent_database"]  # Replace with your database name
        collection = db["llama_agents"] 


        agent_document = {
                "agent_id": str(uuid.uuid4()),
                "agent_name": agent.agent_name,
                "prompt": agent.prompt,
                "llm_config": agent.llm_model
            }
        collection.insert_one(agent_document)

        output = json.dumps({"message": "Llama agent created successfully", "agent": agent_document['agent_id']})
        return output
    except Exception as e:
        return json.dumps({"error": f"An error occurred: {str(e)}"}), 500
    


@app.get("/initializeAgent/{agent_id}")
async def initialize_agent(agent_id):
    try:
        MONGO_URI = "mongodb+srv://sunnymurali:rZPTs1dslFCUbxbh@cluster0.46yro.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        # Change this to your actual URI

        # Create a connection to MongoDB
        client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        db = client["agent_database"]  # Replace with your database name
        collection = db["llama_agents"] 
        
        agent_document = collection.find_one({"agent_id": agent_id})
        
        if not agent_document:
            response = "Agent Not Found"
            return json.dumps({"error": response}), 404
        
        # Convert ObjectId to string for JSON serialization
        agent_document["_id"] = str(agent_document["_id"])
        model = agent_document["llm_config"]
        system_prompt = agent_document["prompt"]
        llm = OpenAI(temperature=0.0,
                      model=model,
                      api_key="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",
                      system_prompt=system_prompt)
        chat_engine = SimpleChatEngine.from_defaults(llm=llm)
        #output = json.dumps({"message": "Llama agent retrieved successfully", "agent": agent_document})
        return chat_engine
    except Exception as e:
        return json.dumps({"error": f"An error occurred: {str(e)}"}), 500

@app.get("/initializeAgent/{agent_id}")
async def initialize_agent(agent_id):
    try:
        MONGO_URI = "mongodb+srv://sunnymurali:rZPTs1dslFCUbxbh@cluster0.46yro.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        # Change this to your actual URI

        # Create a connection to MongoDB
        client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        db = client["agent_database"]  # Replace with your database name
        collection = db["llama_agents"] 
        
        agent_document = collection.find_one({"agent_id": agent_id})
        
        if not agent_document:
            response = "Agent Not Found"
            return json.dumps({"error": response}), 404
        
        # Convert ObjectId to string for JSON serialization
        agent_document["_id"] = str(agent_document["_id"])
        model = agent_document["llm_config"]
        system_prompt = agent_document["prompt"]
        llm = OpenAI(temperature=0.0,
                      model=model,
                      api_key="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",
                      system_prompt=system_prompt)
        chat_engine = SimpleChatEngine.from_defaults(llm=llm)
        #output = json.dumps({"message": "Llama agent retrieved successfully", "agent": agent_document})
        return chat_engine
    except Exception as e:
        return json.dumps({"error": f"An error occurred: {str(e)}"}), 500


@app.post("/initializeAgent/{agent_id}/chat/")
async def chat_agent(agent_id, user_input: str):
    try:
        MONGO_URI = "mongodb+srv://sunnymurali:rZPTs1dslFCUbxbh@cluster0.46yro.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        # Change this to your actual URI
        # Create a connection to MongoDB
        client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        db = client["agent_database"]  # Replace with your database name
        collection = db["llama_agents"] 
        
        agent_document = collection.find_one({"agent_id": agent_id})
        
        if not agent_document:
            response = "Agent Not Found"
            return json.dumps({"error": response}), 404
        
        # Convert ObjectId to string for JSON serialization
        agent_document["_id"] = str(agent_document["_id"])
        model = agent_document["llm_config"]
        system_prompt = agent_document["prompt"]
        llm = OpenAI(temperature=0.0,
                      model=model,
                      api_key="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",
                      system_prompt=system_prompt)
        chat_engine = SimpleChatEngine.from_defaults(llm=llm)
        print(chat_engine)
        response = chat_engine.chat(user_input)
        history = chat_engine.chat_history
        for i in history:
            chat_his_dict = i.dict()
            collection.update_one({"agent_id": "1d440344-8bc8-4b0d-aa9d-8bfa9ca478a0"}, {"$push":{"chat_history":[chat_his_dict]}}, upsert=True)
        #output = json.dumps({"message": "Llama agent retrieved successfully", "agent": agent_document})
        return response
    except Exception as e:
        return json.dumps({"error": f"An error occurred: {str(e)}"}), 500

@app.post("/engine/")
async def rag_questions(query: Question):
    answer = ae.process_query(query.query)
    
    return answer

@app.post("/docUpload/")
async def upload_process(agent_id: str, query: str, uploaded_file: Annotated[UploadFile, File(description="A file read as UploadFile")]):
    
    # Load the PDF
    content = await uploaded_file.read()
    pdf_reader = PyPDF2.PdfReader(uploaded_file.file)
    
    #data = pdf_reader.load()
    docs = []
    text = ""
    i = 1
    for page in pdf_reader.pages:
        docs.append(Document(page_content=page.extract_text(), metadata={'page':i}))
        i += 1
    #split data into chunks 
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents  = text_splitter.split_documents(docs)


    MONGO_URI = "mongodb+srv://sunnymurali:rZPTs1dslFCUbxbh@cluster0.46yro.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    client.admin.command('ping')
    embeddings = OpenAIEmbeddings()
    print("Pinged your deployment. You successfully connected to MongoDB!")
    db = client["agent_database"]  # Replace with your database name
    collection = db["llama_agents"] 
    agent_document = collection.find_one({"agent_id": agent_id})
        
    if not agent_document:
        response = "Agent Not Found"
        return json.dumps({"error": response}), 404
    
    # Convert ObjectId to string for JSON serialization
    agent_document["_id"] = str(agent_document["_id"])
    file_data = {"filename": uploaded_file.filename, "content": docs}
    #Prepare documents for insertion
    docs_to_insert = [{
    "doc_id": str(uuid.uuid4()),
    "text": doc.page_content,
    "embedding": get_embedding(doc.page_content)
    } for doc in documents]
    print(docs_to_insert)
    collection.update_one({"agent_id": "1d440344-8bc8-4b0d-aa9d-8bfa9ca478a0"}, {"$push":{"documents":docs_to_insert}}, upsert=True)

    #collection.insert_many(docs_to_insert)
    print(len(docs_to_insert))
    
    return {"documents ": documents}




    
# Define a function to generate embeddings
def get_embedding(data):
    """Generates vector embeddings for the given data."""
    embeddings = OpenAIEmbeddings()
    embeddings.embed_documents(data)
    #embedding = model.encode(data)
    return embeddings

if __name__ == "__main__":
    _init()
    app.run(debug=True)