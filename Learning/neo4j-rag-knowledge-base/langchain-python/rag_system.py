"""
RAG (Retrieval-Augmented Generation) System for Neo4j Knowledge Base
"""
from typing import List, Optional, Dict, Any
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jRAGSystem:
    """RAG system for querying Neo4j knowledge base"""
    
    def __init__(
        self,
        knowledge_base,
        llm,
        retrieval_k: int = 5,
        enable_hybrid_search: bool = False,
    ):
        """
        Initialize RAG system
        
        Args:
            knowledge_base: Neo4jKnowledgeBase instance
            llm: Language model instance
            retrieval_k: Number of documents to retrieve
            enable_hybrid_search: Use hybrid search instead of pure vector search
        """
        self.kb = knowledge_base
        self.llm = llm
        self.retrieval_k = retrieval_k
        self.enable_hybrid_search = enable_hybrid_search
        
        # Create custom prompt template
        self.prompt_template = self._create_prompt_template()
        
        logger.info("Initialized Neo4j RAG system")
    
    def _create_prompt_template(self) -> PromptTemplate:
        """Create prompt template for RAG"""
        template = """You are a helpful AI assistant that answers questions based on the provided context from a knowledge base.

Context from knowledge base:
{context}

Question: {question}

Instructions:
1. Answer the question based ONLY on the information provided in the context above
2. If the context doesn't contain enough information to answer the question, say "I don't have enough information in the knowledge base to answer this question"
3. Provide specific references to the source documents when possible
4. Be concise but comprehensive in your answer
5. If you're uncertain, express that uncertainty

Answer:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def _retrieve_documents(self, query: str) -> List[Document]:
        """
        Retrieve relevant documents for query
        
        Args:
            query: User query
            
        Returns:
            List of relevant documents
        """
        if self.enable_hybrid_search:
            return self.kb.hybrid_search(query, k=self.retrieval_k)
        else:
            return self.kb.similarity_search(query, k=self.retrieval_k)
    
    def query(
        self,
        question: str,
        return_source_documents: bool = False,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Query the knowledge base using RAG
        
        Args:
            question: User question
            return_source_documents: Whether to return source documents
            verbose: Enable verbose output
            
        Returns:
            Dictionary with answer and optionally source documents
        """
        # Retrieve relevant documents
        documents = self._retrieve_documents(question)
        
        if not documents:
            return {
                "answer": "I couldn't find any relevant information in the knowledge base.",
                "source_documents": [] if return_source_documents else None
            }
        
        # Format context from documents
        context = self._format_context(documents)
        
        # Generate answer using LLM
        prompt = self.prompt_template.format(context=context, question=question)
        
        if verbose:
            logger.info(f"Retrieved {len(documents)} documents")
            logger.info(f"Prompt:\n{prompt}\n")
        
        answer = self.llm.invoke(prompt)
        
        result = {"answer": answer}
        
        if return_source_documents:
            result["source_documents"] = documents
        
        return result
    
    def _format_context(self, documents: List[Document]) -> str:
        """
        Format retrieved documents as context
        
        Args:
            documents: List of Document objects
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown")
            file_name = doc.metadata.get("file_name", "Unknown")
            page = doc.metadata.get("page", "")
            
            header = f"Document {i}"
            if file_name != "Unknown":
                header += f" (Source: {file_name}"
                if page:
                    header += f", Page: {page}"
                header += ")"
            
            context_parts.append(f"{header}:\n{doc.page_content}\n")
        
        return "\n---\n".join(context_parts)
    
    def batch_query(
        self,
        questions: List[str],
        verbose: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Process multiple queries in batch
        
        Args:
            questions: List of questions
            verbose: Enable verbose output
            
        Returns:
            List of results
        """
        results = []
        
        for i, question in enumerate(questions, 1):
            if verbose:
                logger.info(f"Processing query {i}/{len(questions)}: {question}")
            
            result = self.query(question, verbose=verbose)
            results.append(result)
        
        return results
    
    def chat(self, verbose: bool = False):
        """
        Interactive chat interface
        
        Args:
            verbose: Enable verbose output
        """
        print("=" * 80)
        print("Neo4j RAG Knowledge Base - Interactive Chat")
        print("=" * 80)
        print("Type 'exit' or 'quit' to end the session")
        print("Type 'sources' to see source documents with answers")
        print("=" * 80)
        print()
        
        show_sources = False
        
        while True:
            try:
                question = input("\n🤔 You: ").strip()
                
                if not question:
                    continue
                
                if question.lower() in ["exit", "quit", "q"]:
                    print("\n👋 Goodbye!")
                    break
                
                if question.lower() == "sources":
                    show_sources = not show_sources
                    status = "enabled" if show_sources else "disabled"
                    print(f"\n📚 Source documents display {status}")
                    continue
                
                print("\n🤖 Assistant: ", end="", flush=True)
                
                result = self.query(
                    question,
                    return_source_documents=show_sources,
                    verbose=verbose
                )
                
                print(result["answer"])
                
                if show_sources and result.get("source_documents"):
                    print("\n" + "=" * 80)
                    print("📚 Source Documents:")
                    print("=" * 80)
                    
                    for i, doc in enumerate(result["source_documents"], 1):
                        source = doc.metadata.get("file_name", "Unknown")
                        print(f"\n[{i}] {source}")
                        print("-" * 40)
                        preview = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                        print(preview)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error processing query: {e}")
                print(f"\n❌ Error: {str(e)}")


class ConversationalRAG:
    """RAG system with conversation history"""
    
    def __init__(
        self,
        knowledge_base,
        llm,
        retrieval_k: int = 5,
        max_history: int = 5,
    ):
        """
        Initialize conversational RAG
        
        Args:
            knowledge_base: Neo4jKnowledgeBase instance
            llm: Language model instance
            retrieval_k: Number of documents to retrieve
            max_history: Maximum conversation history to maintain
        """
        self.kb = knowledge_base
        self.llm = llm
        self.retrieval_k = retrieval_k
        self.max_history = max_history
        self.conversation_history: List[Dict[str, str]] = []
        
        logger.info("Initialized Conversational RAG system")
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query with conversation context
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer
        """
        # Retrieve relevant documents
        documents = self.kb.similarity_search(question, k=self.retrieval_k)
        
        # Build context with history
        context = self._build_context_with_history(documents)
        
        # Create prompt with history
        prompt = self._create_conversational_prompt(context, question)
        
        # Generate answer
        answer = self.llm.invoke(prompt)
        
        # Update conversation history
        self.conversation_history.append({
            "question": question,
            "answer": answer
        })
        
        # Trim history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        return {
            "answer": answer,
            "source_documents": documents
        }
    
    def _build_context_with_history(self, documents: List[Document]) -> str:
        """Build context including conversation history"""
        context_parts = []
        
        # Add document context
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"Document {i}:\n{doc.page_content}\n")
        
        return "\n---\n".join(context_parts)
    
    def _create_conversational_prompt(self, context: str, question: str) -> str:
        """Create prompt with conversation history"""
        prompt_parts = [
            "You are a helpful AI assistant. Answer questions based on the provided context and conversation history.",
            "\nContext from knowledge base:",
            context,
        ]
        
        if self.conversation_history:
            prompt_parts.append("\nConversation History:")
            for i, exchange in enumerate(self.conversation_history[-3:], 1):
                prompt_parts.append(f"\nQ{i}: {exchange['question']}")
                prompt_parts.append(f"A{i}: {exchange['answer']}")
        
        prompt_parts.append(f"\nCurrent Question: {question}")
        prompt_parts.append("\nAnswer:")
        
        return "\n".join(prompt_parts)
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Cleared conversation history")
