from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import openai

load_dotenv()

MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')
MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
MONGODB_CLUSTER = os.getenv('MONGODB_CLUSTER')
OPENAI_KEY = os.getenv('OPENAI_KEY')
openai.api_key = OPENAI_KEY

uri = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_CLUSTER}/?retryWrites=true&w=majority&appName=Piccolina"
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


db = client['conversation_context']
collection = db['user']

# Generates an embedding for the user's message using OpenAI
def generate_embedding(message):
    response = openai.embeddings.create(
    input=message,
    model="text-embedding-3-small"
    )
    return (response.data[0].embedding)

# Adds the user's message to the database
def add_to_database(discord_id, discord_username, message_content, embedded_msg):
        new_user = {
            "discord_id": discord_id,
            "discord_username": discord_username,
            "message_content": message_content,
            "embedding": embedded_msg
        }
        collection.insert_one(new_user)

# Queries the database for the most similar message to the user's message using vector embeddings
def query_database(discord_id, embedded_msg, msg_content):
    results = db.user.aggregate([{
            "$vectorSearch": {
            "index": "vector_index",
            "path": "embedding",
            "queryVector": embedded_msg,
            "numCandidates": 10,
            "limit": 1
            }
        }])
    
    results_list = list(results)
    
    '''
    for i in results_list:
        print(i["message_content"])'
    '''
    # Returns the message content
    message_contents = [{"type": "text", "text": result["message_content"]} for result in results_list]

    response = [{
        "role": "user",
        "content": message_contents
    }]

    return response
