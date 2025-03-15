import os
import discord
from dotenv import load_dotenv
import openai
import re
import mongo

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_KEY = os.getenv('OPENAI_KEY')
ASSISTANT_ID = os.getenv('ASSISTANT_ID')

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
    embedded_msg = mongo.generate_embedding(message.content)
    
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

    # Queries the database for the most relevant messages to the user's prompt
    results = mongo.query_database(message.author.id, embedded_msg, message.content)
    # Creates a response
    run = openai.beta.threads.runs.create_and_poll(
        thread_id=openAIThreadID,
        assistant_id=ASSISTANT_ID,
        additional_instructions="The following text contains contextual information that you should treat as memory. "
    "Incorporate it naturally into the conversation rather than stating it outright. "
    "Do not explicitly say 'I remember' or repeat it verbatim—just use it like a human recalling past interactions. "
    "You don't need to acknowledge or confirm stored information, just respond naturally and make sure you pay "
    "attention to the context of your preset personality traits. "
    "Here is the relevant context: " + str(results)
    )

    messages = openai.beta.threads.messages.list(openAIThreadID)
    response = messages.data[0].content[0].text.value

    response = re.sub(r'【.*?】', '', response).strip()

    if (len(response) > 1999):
        print("message too long") # Discord char limit - fix later
    
    response = response[:1999]
    await message.channel.send(response)

    #print(f"User ID: ", message.author.id)

    # Adds the user's message to the database to remember for future conversations
    mongo.add_to_database(message.author.id, (await client.fetch_user(message.author.id)).name, message.content, embedded_msg)

    

client.run(TOKEN)