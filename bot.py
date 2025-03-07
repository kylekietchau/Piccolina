import os
import discord
from dotenv import load_dotenv
import openai
import contextualizer
import re

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_KEY = os.getenv('OPENAI_KEY')
ASSISTANT_ID = os.getenv('ASSISTANT_ID')
VECTOR_STORE_ID = os.getenv('VECTOR_STORE_ID')

openai.api_key = OPENAI_KEY

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

threads = {} # Threads are like a conversation to pull context from

def getOpenAiThreadID (discordThreadID):
    return threads[discordThreadID]

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user: # Ignore messages from bots
        return
    discordThreadID = message.channel.id
    
    if discordThreadID not in threads:
        thread = openai.beta.threads.create()
        openAIThreadID = thread.id
        threads[discordThreadID] = openAIThreadID
    else:
        openAIThreadID = threads[discordThreadID]

    openai.beta.threads.messages.create(
        thread_id=openAIThreadID,
        role="user",
        content=message.content
    )

    # Creates a response
    run = openai.beta.threads.runs.create_and_poll(
        thread_id=openAIThreadID,
        assistant_id=ASSISTANT_ID,
    )

    messages = openai.beta.threads.messages.list(openAIThreadID)
    response = messages.data[0].content[0].text.value

    response = re.sub(r'【.*?】', '', response).strip()

    if (len(response) > 1999):
        print("message too long") # Discord char limit - fix later
    
    response = response[:1999]
    await message.channel.send(response)

    # Writes the user's message to a file for the bot to remember indefinitely
    with open("context.txt", "a") as file:
        file.write(f"User: {message.content}\n")

    # Modifies the vector store to include the new context
    contextualizer.modifyVectorStore()
    

client.run(TOKEN)