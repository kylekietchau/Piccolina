# Piccolina

A Discord chat bot that uses the OpenAI assistant API in order to receive and generate prompts from the user on Discord.

The chat bot uses Retrieval-Augmented Generation (RAG) to generate its responses. Embeddings are generated on every message from the user and stored in a MongoDB cluster. It then uses Mongo's Atlas Search to find relevant information using vector search. The relevant messages are then passed
back to the AI to use as contextual information in its response.


## In Progress:
		1. Use NLP to fully optimize the contextual information gathered from the user.
