"""Chatbot package for utility network RAG-based customer service."""

from src.chatbot.chatbot import UtilityNetworkChatbot
from src.chatbot.retriever import UtilityNetworkRetriever
from src.chatbot.embeddings import (
    EmbeddingsGenerator,
    EMBEDDING_CONFIGS,
    get_recommended_model,
    create_embeddings_generator,
    install_instructions
)
from src.chatbot.prompts import (
    SYSTEM_PROMPT,
    create_rag_prompt,
    get_sample_prompts,
    SAMPLE_PROMPTS
)

__all__ = [
    'UtilityNetworkChatbot',
    'UtilityNetworkRetriever',
    'EmbeddingsGenerator',
    'EMBEDDING_CONFIGS',
    'get_recommended_model',
    'create_embeddings_generator',
    'install_instructions',
    'SYSTEM_PROMPT',
    'create_rag_prompt',
    'get_sample_prompts',
    'SAMPLE_PROMPTS'
]
