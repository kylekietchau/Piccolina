import os
from dotenv import load_dotenv
import openai

load_dotenv()
OPENAI_KEY = os.getenv('OPENAI_KEY')
VECTOR_STORE_ID = os.getenv('VECTOR_STORE_ID')

openai.api_key = OPENAI_KEY

def modifyVectorStore():
    # Finds and deletes old file and vector store file from the vector store
    for file_type in openai.files.list(purpose="assistants"):
        if file_type.filename == "context.txt":
            openai.beta.vector_stores.files.delete(
                vector_store_id=VECTOR_STORE_ID,
                file_id=file_type.id
            )
            openai.files.delete(file_type.id)
            break

    # Creates a new file
    updated_context_file = openai.files.create(
        file=open("context.txt", "rb"),
        purpose="assistants"
    )

    # Creates a new vector store file with the file just 
    # created and adds it to the vector store
    openai.beta.vector_stores.files.create(
        vector_store_id=VECTOR_STORE_ID,
        file_id=updated_context_file.id
        )