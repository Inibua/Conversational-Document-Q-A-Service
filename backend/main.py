"""
Main FastAPI application for the Conversational Document Q&A Service.
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

# Import necessary LangChain components
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import SummarizationMiddleware, PIIMiddleware

# Import vector store
from vector_store import QdrantVectorStore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Conversational Document Q&A Service", version="1.0.0")

# In-memory storage for user sessions
checkpointer = InMemorySaver()

# Initialize vector store (with default config for now)
# In a real implementation, you would load this from a config file
vector_store_config = {
    "embedding_model": "default",
    "qdrant_host": os.getenv("QDRANT_HOST", "localhost"),
    "qdrant_port": int(os.getenv("QDRANT_PORT", 6333)),
    "collection_name": os.getenv("QDRANT_COLLECTION", "documents"),
    "vector_size": int(os.getenv("VECTOR_SIZE", 768))
}

vector_store = QdrantVectorStore(vector_store_config)


class HealthResponse(BaseModel):
    """Response model for health endpoint."""
    status_code: int
    text: str


class InvokeRequest(BaseModel):
    """Request model for invoke endpoint."""
    user_id: str
    message: str


class InvokeResponse(BaseModel):
    """Response model for invoke endpoint."""
    status_code: int
    text: str


@tool
def retrieve_from_knowledge_base(query: str) -> str:
    """
    Use this tool to retrieve information from the knowledge base. 
    Input should be a search query.
    
    Args:
        query: User query to search for

    Returns:
        String representation of retrieved chunks
    """
    try:
        # Perform semantic retrieval
        results = vector_store.retrieve_semantic(query, limit=5)
        
        # Format results as a string
        formatted_results = "\n\n".join([
            f"Document ID: {result['id']}\nContent: {result['payload'].get('content', 'N/A')}\nScore: {result['score']}"
            for result in results
        ])
        
        return formatted_results if formatted_results else "No relevant information found."
        
    except Exception as e:
        logger.error(f"Error retrieving from knowledge base: {e}")
        return f"Error retrieving information: {str(e)}"


def get_or_create_agent():
    """
    Get or create an agent for a specific user.
        
    Returns:
        Configured agent
    """
    # Define tools
    tools = [retrieve_from_knowledge_base]
    
    # Initialize LLM
    model = init_chat_model("ollama:gemma4:31b-cloud")  # Using gemma4:31b-cloud as default, can be parameterized
    
    # Create agent
    agent = create_agent(
        model=model,
        tools=tools,
        checkpointer=checkpointer,
        system_prompt="You are a helpful assistant that can answer questions by retrieving information from a knowledge base."
                      "Always make use of the tool, when answering. You must always provide grounded answers. If the"
                      "information from the tool is insufficient, state that the retrieved info is insufficient"
                      "and then try to navigate the use how to phrase the questions better.",
        middleware=[
            SummarizationMiddleware(
                model="ollama:gemma4:31b-cloud",
                trigger=("tokens", 2000),
                keep=("messages", 10),
            ),
            PIIMiddleware(
                pii_type="email",
                strategy="redact",
                apply_to_input=True,
            )
        ]
    )
    
    return agent


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(status_code=200, text="OK")


@app.post("/invoke", response_model=InvokeResponse)
async def invoke(request: InvokeRequest):
    """
    Main endpoint to interact with the LLM agent.
    
    Args:
        request: Invoke request containing user_id and message
        
    Returns:
        Invoke response with LLM's final response
    """
    try:
        # Get or create agent for user
        agent = get_or_create_agent()
        
        # Configuration for the agent with thread_id for memory
        config = {"configurable": {"thread_id": request.user_id}}
        
        # Run agent with user message
        result = agent.invoke(
            {"messages": [{"role": "user", "content": request.message}]},
            config=config
        )
        
        # Extract final response
        # The last message should be the AI's response
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            response_text = "No response generated."
        
        return InvokeResponse(status_code=200, text=response_text)
        
    except Exception as e:
        logger.error(f"Error in invoke endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)