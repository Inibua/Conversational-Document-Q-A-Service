# Backend PRD

## Overview
A simple FastAPI server used as a wrapper around LLM calls. It keeps track of sessions and users and keeps in memory chat history per user.
Provides simple PII and automatic context summarization.

## Requirements
1. Two endpoints:
   * health - status of the server
   * invoke - main endpoint used to interact with an LLM
2. Use create_agent from langchain.
3. Use ChatOllama from langchain.
4. Keeps track of user history in a local dictionary or using the langchains checkpointing mechanism.
5. Has a tool to retrieve from the knowledge base, the knowledge base provider is parametrized. The tool embeds the user query then performs a retrieve_semantic using the vector_store.
6. Has automatic context summarization using langchains SummarizationMiddleware.
7. Has simple PII detection using langchains PIIMiddleware.

## Sequence
1. invoke receives user message.
2. invoke calls the agent
3. The agent receives all previous messages and the new query.
4. The agent calls the tool if necessary.
5. The tool returns the retrieved chunks.
6. The LLM uses the chat history and tool results to formulate an answer.
7. invoke returns the answer (to be used by the frontend)

## APIs
1. health - response is json {status_code: e.g. 200, text:"OK"}
2. invoke - response is json {status_code: e.g. 200, text: LLMs final response message as text}

## Security
Nothing on security side for now

## Deployment
local script run.